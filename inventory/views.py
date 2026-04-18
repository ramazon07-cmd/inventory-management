from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StockMovement
from .serializers import StockMovementSerializer
from .services import add_stock, sell_product, get_product_stock, InsufficientStockError, InvalidInputError
from products.models import Product


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        try:
            movement = add_stock(product_id, quantity)
            return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)
        except (Product.DoesNotExist, InvalidInputError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='sell')
    def sell(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        try:
            movement = sell_product(product_id, quantity)
            return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)
        except (Product.DoesNotExist, InsufficientStockError, InvalidInputError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='check/(?P<product_id>[^/.]+)')
    def check(self, request, product_id=None):
        stock = get_product_stock(int(product_id))
        return Response({'product_id': product_id, 'current_stock': stock})
