from django.db import models
from products.models import Product

# Create your models here.

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} @ {self.price}"