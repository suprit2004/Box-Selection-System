from decimal import Decimal
from django.test import TestCase
from fulfillment.models import Product, ShippingBox, Order, OrderItem, OrderStatus
from fulfillment.services.box_selector import BoxSelectorService
from fulfillment.services.packing_engine import ItemCuboid


class BoxSelectorServiceTest(TestCase):
    def setUp(self):
        # Box A: Small & Cheap ($1.50, max 3 kg)
        self.box_small = ShippingBox.objects.create(
            code="BOX-SM",
            name="Small Box",
            internal_length=Decimal("20.00"),
            internal_width=Decimal("15.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.50")
        )
        # Box B: Medium & Mid-Price ($2.50, max 10 kg)
        self.box_medium = ShippingBox.objects.create(
            code="BOX-MD",
            name="Medium Box",
            internal_length=Decimal("30.00"),
            internal_width=Decimal("20.00"),
            internal_height=Decimal("15.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("2.50")
        )
        # Box C: Large & Expensive ($4.00, max 20 kg)
        self.box_large = ShippingBox.objects.create(
            code="BOX-LG",
            name="Large Box",
            internal_length=Decimal("45.00"),
            internal_width=Decimal("35.00"),
            internal_height=Decimal("25.00"),
            max_weight=Decimal("20.000"),
            cost=Decimal("4.00")
        )

        self.book = Product.objects.create(
            sku="BOOK-1",
            name="Textbook",
            length=Decimal("22.00"),
            width=Decimal("14.00"),
            height=Decimal("4.00"),
            weight=Decimal("1.200")
        )
        self.mug = Product.objects.create(
            sku="MUG-1",
            name="Ceramic Mug",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.400")
        )

    def test_cheapest_feasible_box_selected(self):
        # 1 Textbook (22x14x4 cm) exceeds Small Box (length 20 cm).
        # Both Medium ($2.50) and Large ($4.00) can fit it.
        # System must select Medium because it is cheaper ($2.50 < $4.00).
        item = ItemCuboid(sku="BOOK-1", length=Decimal("22.00"), width=Decimal("14.00"), height=Decimal("4.00"), weight=Decimal("1.200"))
        result = BoxSelectorService.select_box_for_items([(item, 1)])

        self.assertTrue(result.is_success)
        self.assertEqual(result.recommended_box.code, "BOX-MD")
        self.assertEqual(result.box_cost, Decimal("2.50"))

    def test_weight_capacity_rejection(self):
        # A dense heavy item (weight 4.0 kg, dimensions 10x10x10 cm).
        # Fits dimensionally in Small Box, but exceeds Small Box max weight (3.0 kg).
        # Must pick Medium Box (holds up to 10 kg).
        heavy_item = ItemCuboid(sku="LEAD-1", length=Decimal("10.00"), width=Decimal("10.00"), height=Decimal("10.00"), weight=Decimal("4.000"))
        result = BoxSelectorService.select_box_for_items([(heavy_item, 1)])

        self.assertTrue(result.is_success)
        self.assertEqual(result.recommended_box.code, "BOX-MD")

    def test_empty_order_returns_unpackable(self):
        result = BoxSelectorService.select_box_for_items([])
        self.assertFalse(result.is_success)
        self.assertEqual(result.status, OrderStatus.UNPACKABLE)
        self.assertIn("contains no items", result.reason)

    def test_oversized_item_produces_actionable_diagnosis(self):
        # Item length 60 cm exceeds all boxes in stock (max length 45 cm)
        oversized = ItemCuboid(sku="SKI-1", length=Decimal("60.00"), width=Decimal("10.00"), height=Decimal("10.00"), weight=Decimal("2.000"))
        result = BoxSelectorService.select_box_for_items([(oversized, 1)])

        self.assertFalse(result.is_success)
        self.assertEqual(result.status, OrderStatus.UNPACKABLE)
        self.assertIn("Oversized Item", result.reason)

    def test_tie_breaker_minimum_void_volume(self):
        # Create an alternative box with same cost ($2.50) but larger internal volume
        # Medium box volume: 30 * 20 * 15 = 9000 cm³
        # Alt box volume: 32 * 20 * 15 = 9600 cm³
        alt_box = ShippingBox.objects.create(
            code="BOX-MD-ALT",
            name="Medium Alternate",
            internal_length=Decimal("32.00"),
            internal_width=Decimal("20.00"),
            internal_height=Decimal("15.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("2.50")
        )

        item = ItemCuboid(sku="BOOK-1", length=Decimal("22.00"), width=Decimal("14.00"), height=Decimal("4.00"), weight=Decimal("1.200"))
        result = BoxSelectorService.select_box_for_items([(item, 1)])

        # Must pick BOX-MD because 9000 cm³ < 9600 cm³ (tighter fit, less void volume)
        self.assertEqual(result.recommended_box.code, "BOX-MD")

    def test_recommend_for_order_end_to_end(self):
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.book, quantity=1)
        OrderItem.objects.create(order=order, product=self.mug, quantity=2)

        result = BoxSelectorService.recommend_for_order(order)
        order.refresh_from_db()

        self.assertTrue(result.is_success)
        self.assertEqual(order.status, OrderStatus.OPTIMIZED)
        self.assertIsNotNone(order.recommended_box)
        self.assertEqual(order.recommended_box.code, "BOX-MD")
        # Total weight: 1.200 + 2 * 0.400 = 2.000 kg
        self.assertEqual(order.total_weight, Decimal("2.000"))
        self.assertIn("Selected Medium Box", order.packing_notes)

