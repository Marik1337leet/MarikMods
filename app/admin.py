from fastapi import FastAPI, Request, UploadFile, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, shutil
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base, Product, Order
from .repo import list_products, get_order
from .config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GTA5 Mod Shop Admin")
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.id.desc()).all()
    orders = db.query(Order).order_by(Order.id.desc()).limit(20).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "orders": orders, "settings": settings})

@app.get("/products/new", response_class=HTMLResponse)
async def new_product(request: Request):
    return templates.TemplateResponse("product_form.html", {"request": request, "product": None})

@app.post("/products/create")
async def create_product(title: str = Form(...), description: str = Form(""), price_stars: int = Form(...), price_usd: float = Form(...), file: UploadFile = Form(...), db: Session = Depends(get_db)):
    path = os.path.join("app", "uploads", file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    p = Product(title=title, description=description, price_stars=price_stars, price_usd=price_usd, file_path=path)
    db.add(p); db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    return templates.TemplateResponse("order_detail.html", {"request": request, "order": order})
