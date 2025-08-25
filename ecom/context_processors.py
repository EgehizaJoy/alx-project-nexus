import json
from django.conf import settings
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
    
# context_processors.py (create this file in your app directory)


def cart_count(request):
    count = 0
    if 'cart_data' in request.COOKIES:
        try:
            cart_data = json.loads(request.COOKIES['cart_data'])
            count = sum(int(qty) for qty in cart_data.values())
        except (json.JSONDecodeError, ValueError):
            count = 0
    # Fallback to old format
    elif 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids:
            count = len(product_ids.split('|'))
    
    return {'cart_count': count}