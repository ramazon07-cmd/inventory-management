from django.db import models, transaction
from products.models import Product
from .models import StockMovement


class InsufficientStockError(Exception):
    pass


class InvalidInputError(Exception):
    pass


def validate_quantity(quantity):
    if not isinstance(quantity, int) or quantity <= 0:
        raise InvalidInputError("Quantity must be a positive integer")


def get_product_stock(product_id: int) -> int:
    """Calculate current stock: SUM(IN) - SUM(OUT)"""
    stock_in = StockMovement.objects.filter(
        product_id=product_id, movement_type=StockMovement.IN
    ).aggregate(total=models.Sum('quantity'))['total'] or 0
    stock_out = StockMovement.objects.filter(
        product_id=product_id, movement_type=StockMovement.OUT
    ).aggregate(total=models.Sum('quantity'))['total'] or 0
    return stock_in - stock_out


@transaction.atomic
def add_stock(product_id: int, quantity: int) -> StockMovement:
    validate_quantity(quantity)
    product = Product.objects.get(id=product_id)
    return StockMovement.objects.create(
        product=product,
        quantity=quantity,
        movement_type=StockMovement.IN
    )


@transaction.atomic
def sell_product(product_id: int, quantity: int) -> StockMovement:
    validate_quantity(quantity)
    current_stock = get_product_stock(product_id)
    if current_stock < quantity:
        raise InsufficientStockError(f"Not enough stock. Available: {current_stock}")
    product = Product.objects.get(id=product_id)
    return StockMovement.objects.create(
        product=product,
        quantity=quantity,
        movement_type=StockMovement.OUT
    )
