from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Q
from inventory.models import StockMovement
from sales.models import Order
from products.models import Product


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    from django.utils import timezone

    today = timezone.now().date()

    # Orders today
    orders_today = Order.objects.filter(created_at__date=today).count()

    # Revenue today
    orders_today_qs = Order.objects.filter(created_at__date=today).prefetch_related('items')
    revenue_today = sum(
        sum(item.quantity * item.price for item in order.items.all())
        for order in orders_today_qs
    )

    # Top products - by total sold (OUT movements)
    top_products = Product.objects.annotate(
        total_sold=Sum(
            'stockmovement__quantity',
            filter=Q(stockmovement__movement_type=StockMovement.OUT)
        )
    ).exclude(total_sold__isnull=True).order_by('-total_sold')[:5]

    # Low stock
    from inventory.selectors import get_low_stock_products
    low_stock = get_low_stock_products(10)

    return Response({
        'orders_today': orders_today,
        'revenue_today': float(revenue_today),
        'top_products': [{'id': p.id, 'name': p.name, 'total_sold': p.total_sold} for p in top_products],
        'low_stock': [{'id': item['product'].id, 'name': item['product'].name, 'stock': item['stock']} for item in low_stock],
    })
