from fastapi import FastAPI
from telegram.ext import Application
import asyncio

root = FastAPI()

# создаём приложение Telegram бота
telegram_app = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

# Lifespan вместо on_event
@root.on_event("startup")
async def startup():
    print("Запуск бота...")
    asyncio.create_task(telegram_app.run_polling())

@root.on_event("shutdown")
async def shutdown():
    print("Остановка бота...")
    await telegram_app.shutdown()

@root.get("/")
async def home():
    return {"status": "ok", "message": "FastAPI + Telegram bot работает 🚀"}
