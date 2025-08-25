from threading import Thread
import uvicorn
from app.bot import start_bot
from app.admin import app as fastapi_app
from app.admin import app as admin_app
from app.payments.cryptocloud import router as cc_router
from app.config import settings
from app.bot import build_application


if __name__ == "__main__":
    # Запуск бота в отдельном потоке
    Thread(target=start_bot, daemon=True).start()
    # Запуск FastAPI
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)
