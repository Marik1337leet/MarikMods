from threading import Thread
import uvicorn
from app.bot import start_bot
from app.admin import app as fastapi_app

if __name__ == "__main__":
    # Запуск бота в отдельном потоке
    Thread(target=start_bot, daemon=True).start()
    # Запуск FastAPI
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)
