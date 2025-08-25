from telegram import LabeledPrice

def build_stars_prices(product_title: str, amount_stars: int):
    return [LabeledPrice(label=product_title, amount=amount_stars)]

def format_receipt(product, order_id: int) -> str:
    return f"<b>Спасибо!</b>\nВаш заказ №{order_id} — {product.title}"
