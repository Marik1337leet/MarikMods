import os
from dataclasses import dataclass

def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name, str(default)).strip().lower()
    return v in ("1","true","yes","on")

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8293359104:AAHrvnTH88MPOABGTVGzZpAj2Dz4bp2UkNc")
    ADMIN_TELEGRAM_ID: int = int(os.getenv("ADMIN_TELEGRAM_ID", "5810097604"))
    PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8080")
    PORT: int = int(os.getenv("PORT", "8080"))
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./app.db")

    ENABLE_STARS: bool = _env_bool("ENABLE_STARS", True)
    ENABLE_CRYPTOCLOUD: bool = _env_bool("ENABLE_CRYPTOCLOUD", True)

    CRYPTOCLOUD_API_KEY: str = os.getenv("CRYPTOCLOUD_API_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiTmpnek1EUT0iLCJ0eXBlIjoicHJvamVjdCIsInYiOiJjMDJlMWIzYzc0YThjYWE3NWY1MTIxM2I3NmNmNjdmYjI5NTBlMWM1NjZmNDk0ODA1NzczMmViOTdlOGYyNGIyIiwiZXhwIjo4ODE1NTg3MDc0OH0.k_7E9NuXGNb6oxkRxLuXJnB8FkL0tJ84xKPPbd8AexY")
    CRYPTOCLOUD_SHOP_ID: str = os.getenv("CRYPTOCLOUD_SHOP_ID", "LiNHwZ279uZWP1MD")
    CRYPTOCLOUD_WEBHOOK_SECRET: str = os.getenv("CRYPTOCLOUD_WEBHOOK_SECRET", "yuKYebBV4r1k8NJSRN221Cyqiq1BdEcp26dp")

settings = Settings()
