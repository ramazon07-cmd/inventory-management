from django.db import models
from django.db.models import Sum
from products.models import Product
from .models import StockMovement
from .services import get_product_stock


def get_stock_movements(product_id=None, movement_type=None):
    qs = StockMovement.objects.all()
    if product_id:
        qs = qs.filter(product_id=product_id)
    if movement_type:
        qs = qs.filter(movement_type=movement_type)
    return qs


def get_product_current_stock(product_id: int) -> int:
    return get_product_stock(product_id)


def get_low_stock_products(threshold: int = 10):
    """Products with stock below threshold"""
    products = Product.objects.all()
    low_stock = []
    for product in products:
        stock = get_product_current_stock(product.id)
        if stock <= threshold:
            low_stock.append({'product': product, 'stock': stock})
    return low_stock


def get_top_selling_products(limit: int = 5):
    """Most sold products by total OUT quantity"""
    return Product.objects.annotate(
        total_sold=Sum(
            'stockmovement__quantity',
            filter=models.Q(stockmovement__movement_type=StockMovement.OUT)
        )
    ).exclude(total_sold__isnull=True).order_by('-total_sold')[:limit]
