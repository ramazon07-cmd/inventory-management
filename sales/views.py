from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Order
from .serializers import OrderSerializer
from .services import create_order


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        items = request.data.get('items', [])
        try:
            order = create_order(items)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        orders = Order.objects.all().prefetch_related('items').order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)

    @action(detail=False, methods=['get'], url_path='daily')
    def daily(self, request):
        today = timezone.now().date()
        count = Order.objects.filter(created_at__date=today).count()
        return Response({'date': today, 'order_count': count})
