import json
from .models import Product  # adjust path to your Product model

def cart_item_count(request):
    cart_data = request.COOKIES.get('cart', '{}')
    try:
        cart = json.loads(cart_data)
    except json.JSONDecodeError:
        cart = {}

    # Count total quantity across all items
    count = sum(cart.values())
    return {"cart_count": count}

def product_count_in_cart(request):
    cart_data = request.COOKIES.get('cart', '{}')
    try:
        cart = json.loads(cart_data)
    except Exception:
        cart = {}

    # This will count *all quantities*, not just unique items
    count = sum(cart.values())
    return {"product_count_in_cart": count}
    
