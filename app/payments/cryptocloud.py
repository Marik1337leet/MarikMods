import requests, jwt, time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..config import settings
from ..db import SessionLocal
from .. import repo

router = APIRouter()

API_URL = "https://api.cryptocloud.plus/v2/invoice/create"

def create_invoice(amount_usd: float, order_id: str) -> dict:
    headers = {
        "Authorization": f"Token {settings.CRYPTOCLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "amount": round(float(amount_usd), 2),
        "shop_id": settings.CRYPTOCLOUD_SHOP_ID,
        "currency": "USD",
        "order_id": order_id,
    }
    r = requests.post(API_URL, headers=headers, json=data, timeout=20)
    r.raise_for_status()
    resp = r.json()
    if resp.get("status") != "success":
        raise RuntimeError(f"CryptoCloud error: {resp}")
    return resp["result"]

class Postback(BaseModel):
    status: str
    invoice_id: str | None = None
    amount_crypto: float | None = None
    currency: str | None = None
    order_id: str | None = None
    token: str

@router.post("/cryptocloud/postback")
async def cryptocloud_postback(pb: Postback, request: Request):
    # Verify JWT token
    try:
        payload = jwt.decode(pb.token, settings.CRYPTOCLOUD_WEBHOOK_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid signature")
    if payload.get("exp") and int(payload["exp"]) < int(time.time()):
        raise HTTPException(status_code=401, detail="Expired token")

    if pb.status != "success" or not pb.order_id:
        return JSONResponse({"ok": True})

    db = SessionLocal()
    try:
        order = repo.get_order_by_external(db, pb.order_id)
        if order and order.status == "pending":
            repo.mark_paid(db, order.id)
        return JSONResponse({"ok": True})
    finally:
        db.close()
