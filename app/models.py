from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .db import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price_stars: Mapped[int] = mapped_column(Integer, default=100)  # XTR
    price_usd: Mapped[float] = mapped_column(Float, default=1.99)   # for CryptoCloud
    file_path: Mapped[str] = mapped_column(String(400), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), default="")
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    payment_method: Mapped[str] = mapped_column(String(30))  # 'stars' | 'cryptocloud'
    status: Mapped[str] = mapped_column(String(30), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    external_id: Mapped[str] = mapped_column(String(120), default="")  # CryptoCloud order_id
    invoice_link: Mapped[str] = mapped_column(String(500), default="")

    product = relationship("Product")
