from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models
from datetime import datetime

def list_products(db: Session):
    return db.scalars(select(models.Product).where(models.Product.is_active==True).order_by(models.Product.id.desc())).all()

def get_product(db: Session, product_id: int):
    return db.get(models.Product, product_id)

def create_order(db: Session, *, user_id: int, username: str, product_id: int, payment_method: str, external_id: str = "", invoice_link: str = ""):
    order = models.Order(user_id=user_id, username=username or "", product_id=product_id,
                         payment_method=payment_method, external_id=external_id, invoice_link=invoice_link)
    db.add(order); db.commit(); db.refresh(order)
    return order

def mark_paid(db: Session, order_id: int):
    order = db.get(models.Order, order_id)
    if order:
        order.status = "paid"; order.updated_at = datetime.utcnow()
        db.commit(); db.refresh(order)
    return order

def mark_delivered(db: Session, order_id: int):
    order = db.get(models.Order, order_id)
    if order:
        order.status = "delivered"; order.updated_at = datetime.utcnow()
        db.commit(); db.refresh(order)
    return order

def mark_canceled(db: Session, order_id: int):
    order = db.get(models.Order, order_id)
    if order:
        order.status = "canceled"; order.updated_at = datetime.utcnow()
        db.commit(); db.refresh(order)
    return order

def get_order_by_external(db: Session, external_id: str):
    return db.scalars(select(models.Order).where(models.Order.external_id == external_id)).first()

def get_order(db: Session, order_id: int):
    return db.get(models.Order, order_id)
