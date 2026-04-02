from django.db import models

# Create your models here.

class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"

    MOVEMENT_TYPE = [
        (IN, "Stock In"),
        (OUT, "Stock Out"),
    ]

    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} - {self.quantity}"