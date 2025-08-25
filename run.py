import os
import asyncio
from fastapi import FastAPI
from telegram.ext import Application

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Запуск бота...")
    await telegram_app.initialize()
    asyncio.create_task(telegram_app.start())
    asyncio.create_task(telegram_app.updater.start_polling())

@app.on_event("shutdown")
async def shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()
