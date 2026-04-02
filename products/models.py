from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to='product_photos/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()

    def __str__(self):
        return self.name