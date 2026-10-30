from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from fulfillment.models import Product, ShippingBox, Order, OrderItem, OrderStatus


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            sku="BOOK-01",
            name="Python Cookbook",
            length=Decimal("24.00"),
            width=Decimal("18.00"),
            height=Decimal("4.00"),
            weight=Decimal("1.250")
        )

    def test_product_volume_calculation(self):
        # 24 * 18 * 4 = 1728
        self.assertEqual(self.product.volume, Decimal("1728.00"))

    def test_product_sorted_dimensions(self):
        self.assertEqual(
            self.product.sorted_dimensions,
            (Decimal("4.00"), Decimal("18.00"), Decimal("24.00"))
        )

    def test_product_validation_rejects_non_positive_dimension(self):
        invalid_product = Product(
            sku="INVALID-01",
            name="Ghost Item",
            length=Decimal("-5.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.00")
        )
        with self.assertRaises(ValidationError):
            invalid_product.clean()

    def test_product_validation_rejects_zero_weight(self):
        invalid_product = Product(
            sku="INVALID-02",
            name="Zero Weight Item",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.000")
        )
        with self.assertRaises(ValidationError):
            invalid_product.clean()


class ShippingBoxModelTest(TestCase):
    def setUp(self):
        self.box = ShippingBox.objects.create(
            code="BOX-MED",
            name="Medium Parcel",
            internal_length=Decimal("30.00"),
            internal_width=Decimal("20.00"),
            internal_height=Decimal("15.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("2.50")
        )

    def test_box_volume_calculation(self):
        # 30 * 20 * 15 = 9000
        self.assertEqual(self.box.internal_volume, Decimal("9000.00"))

    def test_box_validation_rejects_negative_cost(self):
        invalid_box = ShippingBox(
            code="BOX-NEG",
            name="Negative Cost Box",
            internal_length=Decimal("10.00"),
            internal_width=Decimal("10.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("-1.00")
        )
        with self.assertRaises(ValidationError):
            invalid_box.clean()


class OrderModelTest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            sku="PROD-A",
            name="Item A",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        self.product2 = Product.objects.create(
            sku="PROD-B",
            name="Item B",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.500")
        )
        self.order = Order.objects.create()

    def test_order_totals_calculation(self):
        OrderItem.objects.create(order=self.order, product=self.product1, quantity=2)
        OrderItem.objects.create(order=self.order, product=self.product2, quantity=3)

        self.order.update_totals_from_items()
        self.order.save()

        # Weight: 2 * 1.000 + 3 * 0.500 = 3.500 kg
        self.assertEqual(self.order.total_weight, Decimal("3.500"))

        # Volume: 2 * (10*10*10 = 1000) + 3 * (20*10*5 = 1000) = 5000.00 cm³
        self.assertEqual(self.order.total_volume, Decimal("5000.00"))

    def test_duplicate_product_in_same_order_rejected(self):
        OrderItem.objects.create(order=self.order, product=self.product1, quantity=1)
        with self.assertRaises(IntegrityError):
            OrderItem.objects.create(order=self.order, product=self.product1, quantity=2)

