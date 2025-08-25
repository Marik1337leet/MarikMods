import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .admin import app as admin_app
from .payments.cryptocloud import router as cc_router
from .config import settings
from .bot import build_application

root = FastAPI(title="GTA5 Mod Shop")
root.include_router(cc_router)
root.mount("/", admin_app)

root.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_app = build_application()

@root.on_event("startup")
async def _run_bot():
    await bot_app.initialize()
    asyncio.create_task(bot_app.start())

@root.on_event("shutdown")
async def _stop_bot():
    await bot_app.stop()
    await bot_app.shutdown()

if __name__ == "__main__":
    uvicorn.run("app.main:root", host="0.0.0.0", port=settings.PORT, reload=False)
