import asyncio, secrets
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters
from sqlalchemy.orm import Session
from .config import settings
from .db import SessionLocal, engine
from .models import Base
from . import repo
from .payments.stars import build_stars_prices, format_receipt
from .payments.cryptocloud import create_invoice

Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    return SessionLocal()

def products_kb(db: Session):
    rows = []
    for p in repo.list_products(db):
        rows.append([InlineKeyboardButton(f"{p.title} — {p.price_stars}⭐ / ${p.price_usd:.2f}", callback_data=f"buy:{p.id}")])
    if not rows:
        rows = [[InlineKeyboardButton("Каталог пуст", callback_data="noop")]]
    return InlineKeyboardMarkup(rows)

# ------------------- Обработчики -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    await update.message.reply_text(
        "Добро пожаловать в магазин модов GTA 5! Выберите мод из каталога:",
        reply_markup=products_kb(db)
    )
    db.close()

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    chat = update.effective_chat
    await context.bot.send_message(chat.id, "Каталог:", reply_markup=products_kb(db))
    db.close()

async def handle_buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    query = update.callback_query
    await query.answer()
    _, pid = query.data.split(":")
    product = repo.get_product(db, int(pid))
    if not product:
        await query.edit_message_text("Товар не найден.")
        db.close()
        return

    buttons = []
    if settings.ENABLE_STARS:
        buttons.append([InlineKeyboardButton(f"Оплатить звёздами ⭐ ({product.price_stars})", callback_data=f"paystars:{product.id}")])
    if settings.ENABLE_CRYPTOCLOUD:
        buttons.append([InlineKeyboardButton(f"Криптовалютой (CryptoCloud) — ${product.price_usd:.2f}", callback_data=f"paycc:{product.id}")])
    buttons.append([InlineKeyboardButton("Оплатить «подарком» (инфо)", callback_data=f"giftsinfo")])

    await query.edit_message_text(
        f"<b>{product.title}</b>\n{product.description}\n\nВыберите способ оплаты:",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    db.close()

async def pay_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    query = update.callback_query
    await query.answer()
    _, pid = query.data.split(":")
    product = repo.get_product(db, int(pid))
    user = update.effective_user
    order = repo.create_order(db, user_id=user.id, username=user.username or "", product_id=product.id, payment_method="stars")
    prices = build_stars_prices(product.title, product.price_stars)

    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=product.title,
        description=product.description[:200],
        payload=str(order.id),
        provider_token="",  # empty for Stars
        currency="XTR",
        prices=prices,
        start_parameter=f"order_{order.id}",
        max_tip_amount=0,
        is_flexible=False,
        need_name=False,
        need_email=False
    )
    db.close()

async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    sp = update.message.successful_payment
    order_id = int(sp.invoice_payload)
    order = repo.mark_paid(db, order_id)
    if not order:
        db.close(); return
    product = repo.get_product(db, order.product_id)
    try:
        await update.message.reply_document(document=InputFile(product.file_path),
                                            caption=format_receipt(product, order.id), parse_mode=ParseMode.HTML)
        repo.mark_delivered(db, order.id)
    except Exception:
        await update.message.reply_text("Файл не найден на сервере, свяжитесь с поддержкой.")
    db.close()

async def pay_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    query = update.callback_query
    await query.answer()
    _, pid = query.data.split(":")
    product = repo.get_product(db, int(pid))
    user = update.effective_user
    ext_id = f"TG{user.id}-{pid}-{secrets.token_hex(4)}"
    try:
        invoice = create_invoice(product.price_usd, ext_id)
        order = repo.create_order(db, user_id=user.id, username=user.username or "", product_id=product.id,
                                  payment_method="cryptocloud", external_id=ext_id, invoice_link=invoice.get("link",""))
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Перейти к оплате", url=invoice["link"])]])
        await query.edit_message_text(
            f"Счёт создан на сумму ${product.price_usd:.2f}. Оплатите по ссылке ниже, затем вернитесь в чат — бот пришлёт файл после подтверждения.",
            reply_markup=kb
        )
    except Exception as e:
        await query.edit_message_text(f"Ошибка создания счёта: {e}")
    finally:
        db.close()

async def gifts_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    msg = (
        "Оплата «подарками» в ботах сейчас недоступна через Bot API. "
        "Подарки предназначены для пользователей/каналов и могут быть конвертированы в Stars владельцем. "
        "Для покупок внутри бота используйте ⭐ Stars или крипто-счёт (вне Telegram)."
    )
    await q.edit_message_text(msg)

# ------------------- Создание приложения -------------------

def build_application():
    if not settings.BOT_TOKEN:
        print("Ошибка: BOT_TOKEN пустой!")
        return None

    app = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", show_products))
    app.add_handler(CallbackQueryHandler(handle_buy_cb, pattern=r"^buy:\d+$"))
    app.add_handler(CallbackQueryHandler(pay_stars, pattern=r"^paystars:\d+$"))
    app.add_handler(CallbackQueryHandler(pay_cc, pattern=r"^paycc:\d+$"))
    app.add_handler(CallbackQueryHandler(gifts_info, pattern=r"^giftsinfo$"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    return app

def start_bot():
    app = build_application()
    if app is None:
        print("Ошибка: build_application() вернул None")
        return

    # Создаём цикл событий для текущего потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запуск бота (run_polling — асинхронный)
    loop.run_until_complete(app.run_polling())
