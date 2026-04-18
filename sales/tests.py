from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product
from inventory.models import StockMovement
from inventory.services import add_stock, get_product_stock
from sales.models import Order, OrderItem
from sales.services import create_order

User = get_user_model()


class SalesServiceTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product1 = Product.objects.create(
            name="Product 1",
            description="Test",
            price=100.00,
            category=self.category,
        )
        self.product2 = Product.objects.create(
            name="Product 2",
            description="Test",
            price=50.00,
            category=self.category,
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            role="ADMIN",
        )
        # Add initial stock
        add_stock(self.product1.id, 100)
        add_stock(self.product2.id, 50)

    def test_create_order_creates_order_and_deducts_stock(self):
        """Creating an order should create Order, OrderItems, and deduct stock"""
        items = [
            {'product_id': self.product1.id, 'quantity': 2, 'price': 100.00},
            {'product_id': self.product2.id, 'quantity': 1, 'price': 50.00},
        ]

        order = create_order(items)

        # Check order was created
        self.assertIsNotNone(order.id)
        self.assertEqual(Order.objects.count(), 1)

        # Check order items were created
        self.assertEqual(OrderItem.objects.count(), 2)

        # Check stock was deducted
        self.assertEqual(get_product_stock(self.product1.id), 98)
        self.assertEqual(get_product_stock(self.product2.id), 49)

    def test_create_order_calculates_total(self):
        """Order total should be calculated correctly"""
        items = [
            {'product_id': self.product1.id, 'quantity': 2, 'price': 100.00},
        ]

        order = create_order(items)
        order.refresh_from_db()

        # Calculate total manually
        total = sum(
            item.quantity * item.price
            for item in order.items.all()
        )
        self.assertEqual(total, 200.00)

    def test_order_item_links_to_correct_product(self):
        """OrderItem should link to correct product"""
        items = [
            {'product_id': self.product1.id, 'quantity': 1, 'price': 100.00},
        ]

        order = create_order(items)
        order_item = order.items.first()

        self.assertEqual(order_item.product, self.product1)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(float(order_item.price), 100.00)

    def test_create_order_raises_error_on_insufficient_stock(self):
        """Creating order with insufficient stock should raise error"""
        items = [
            {'product_id': self.product1.id, 'quantity': 200, 'price': 100.00},  # Only 100 in stock
        ]

        from inventory.services import InsufficientStockError
        with self.assertRaises(InsufficientStockError):
            create_order(items)

        # Verify order was NOT created (transaction should rollback)
        self.assertEqual(Order.objects.count(), 0)
