from django.db import transaction
from .models import Order, OrderItem
from inventory.services import sell_product


@transaction.atomic
def create_order(items):
    """
    items: [{'product_id': int, 'quantity': int, 'price': Decimal}, ...]
    Creates order and deducts stock for each item.
    """
    order = Order.objects.create()
    for item in items:
        sell_product(item['product_id'], item['quantity'])
        OrderItem.objects.create(
            order=order,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item.get('price', 0)
        )
    return order
