from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product
from inventory.models import StockMovement
from inventory.services import (
    add_stock,
    sell_product,
    get_product_stock,
    InsufficientStockError,
    InvalidInputError,
)

User = get_user_model()


class InventoryServiceTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=100.00,
            category=self.category,
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            role="ADMIN",
        )

    def test_add_stock_increases_stock(self):
        """Adding stock should increase the current stock"""
        initial_stock = get_product_stock(self.product.id)
        self.assertEqual(initial_stock, 0)

        add_stock(self.product.id, 50)

        new_stock = get_product_stock(self.product.id)
        self.assertEqual(new_stock, 50)

    def test_add_stock_creates_movement(self):
        """Adding stock should create a StockMovement record"""
        movement = add_stock(self.product.id, 30)

        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.quantity, 30)
        self.assertEqual(movement.movement_type, StockMovement.IN)

    def test_sell_product_decreases_stock(self):
        """Selling should decrease the current stock"""
        add_stock(self.product.id, 100)
        initial_stock = get_product_stock(self.product.id)
        self.assertEqual(initial_stock, 100)

        sell_product(self.product.id, 30)

        new_stock = get_product_stock(self.product.id)
        self.assertEqual(new_stock, 70)

    def test_sell_product_creates_movement(self):
        """Selling should create an OUT StockMovement record"""
        add_stock(self.product.id, 50)
        movement = sell_product(self.product.id, 20)

        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.quantity, 20)
        self.assertEqual(movement.movement_type, StockMovement.OUT)

    def test_sell_product_raises_insufficient_stock(self):
        """Selling more than available stock should raise InsufficientStockError"""
        add_stock(self.product.id, 10)

        with self.assertRaises(InsufficientStockError):
            sell_product(self.product.id, 20)

    def test_add_stock_invalid_quantity_raises_error(self):
        """Adding invalid quantity should raise InvalidInputError"""
        with self.assertRaises(InvalidInputError):
            add_stock(self.product.id, 0)

        with self.assertRaises(InvalidInputError):
            add_stock(self.product.id, -5)

    def test_sell_product_invalid_quantity_raises_error(self):
        """Selling invalid quantity should raise InvalidInputError"""
        with self.assertRaises(InvalidInputError):
            sell_product(self.product.id, 0)

        with self.assertRaises(InvalidInputError):
            sell_product(self.product.id, -5)

    def test_multiple_adds_and_sells(self):
        """Multiple add and sell operations should calculate correctly"""
        add_stock(self.product.id, 100)
        add_stock(self.product.id, 50)
        self.assertEqual(get_product_stock(self.product.id), 150)

        sell_product(self.product.id, 30)
        self.assertEqual(get_product_stock(self.product.id), 120)

        sell_product(self.product.id, 20)
        self.assertEqual(get_product_stock(self.product.id), 100)

    def test_product_not_found_raises_error(self):
        """Operating on non-existent product should raise error"""
        import uuid
        fake_id = max(p.id for p in Product.objects.all()) + 1

        with self.assertRaises(Product.DoesNotExist):
            add_stock(fake_id, 10)
