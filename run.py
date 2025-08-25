import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin import app as admin_app
from app.payments.cryptocloud import router as cc_router
from app.bot import build_application

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
