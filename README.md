# Telegram-магазин модов GTA5 (Stars + CryptoCloud)

Готовый проект: Бот Telegram с оплатой **Telegram Stars (XTR)** для цифровых товаров и **криптовалютой через CryptoCloud** (вне Telegram) + простая админка и каталог на FastAPI.

> ⚠️ Важно по правилам Telegram: для продажи **цифровых** товаров **внутри приложений Telegram** нужно использовать **Stars** (`XTR`). Для криптоплатежей можно давать внешнюю ссылку на оплату в браузере, но Telegram может ограничить показ бота в мобильных клиентах. Используйте на свой риск.

## Быстрый старт

1. Установите зависимости (Python 3.11+):
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Скопируйте `.env.example` в `.env` и заполните:
   - `BOT_TOKEN` — токен бота от @BotFather
   - `ADMIN_TELEGRAM_ID` — ваш аккаунт
   - `PUBLIC_BASE_URL` — публичный URL FastAPI (домен или Ngrok)
   - `CRYPTOCLOUD_API_KEY`, `CRYPTOCLOUD_SHOP_ID`, `CRYPTOCLOUD_WEBHOOK_SECRET`
   - Флаги `ENABLE_STARS`, `ENABLE_CRYPTOCLOUD`
3. Запуск:
   ```bash
   python -m app.main
   ```
   Админка/каталог: `http://localhost:8080/`

4. Добавьте товары в админке (название, описание, цена и файл мода).

## Оплата Stars (XTR)
- Бот создаёт инвойс `currency='XTR'` (без `provider_token`). После `successful_payment` файл отправляется покупателю автоматически.

## Оплата CryptoCloud
- Бот создаёт счёт через API и отдаёт ссылку.
- В CryptoCloud в проекте укажите URL уведомлений: `https://ВАШ-ДОМЕН/cryptocloud/postback` и секрет `CRYPTOCLOUD_WEBHOOK_SECRET`.
- После подтверждения оплаты заказ помечается как `paid`. Бот отправит файл, как только пользователь напишет следующее сообщение (или расширьте логику на авторассылку).

## Telegram Gifts (подарки)
В ботах нет прямой приёмки «подарков» как оплаты. Это механизм для пользователей/каналов и он не доступен в Bot API как способ оплаты.

## Структура
- `app/main.py` — FastAPI + запуск бота
- `app/bot.py` — логика бота
- `app/payments/` — интеграции (Stars, CryptoCloud)
- `app/admin.py` + `app/templates/` — админка/каталог
- `app/uploads/` — файлы модов
- `app/models.py`, `app/db.py`, `app/repo.py` — SQLite

## Продакшен
- Используйте HTTPS (например, nginx + certbot).
- Ограничьте доступ к админке (BasicAuth/IP allowlist).
- Храните ключи в `.env` и не публикуйте.
"# MarikMods" 
