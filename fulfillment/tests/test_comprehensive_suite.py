"""
Comprehensive Automated Test Suite for AI-Assisted Box Selection System.

Covers the 15 mandatory test categories:
1. Product model validation
2. Shipping box model validation
3. Order and OrderItem relationships
4. Total order weight calculation
5. Product dimensional feasibility
6. Product rotation
7. Multiple products
8. Multiple quantities of the same product
9. Weight capacity exceeded
10. No suitable box available
11. Empty order
12. Invalid dimensions
13. Zero or negative values
14. Multiple eligible boxes with different costs
15. Orders containing oversized products
"""

from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from fulfillment.models import Product, ShippingBox, Order, OrderItem, OrderStatus
from fulfillment.services.packing_engine import PackingEngine, BoxSpec, ItemCuboid, PlacedCuboid
from fulfillment.services.box_selector import BoxSelectorService, BoxSelectionResult


class ComprehensiveBoxSelectionTestSuite(TestCase):
    """
    Integration and unit tests verifying end-to-end correctness of the
    Box Selection engine and Django data layer across all 15 business categories.
    """

    def setUp(self):
        """Seed realistic warehouse boxes and products for test scenarios."""
        # Standard warehouse carton catalog
        self.box_small = ShippingBox.objects.create(
            code="BOX-S",
            name="Small Parcel Carton",
            internal_length=Decimal("22.00"),
            internal_width=Decimal("16.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.25"),
            is_active=True
        )
        self.box_medium = ShippingBox.objects.create(
            code="BOX-M",
            name="Medium Shipping Box",
            internal_length=Decimal("32.00"),
            internal_width=Decimal("24.00"),
            internal_height=Decimal("16.00"),
            max_weight=Decimal("8.000"),
            cost=Decimal("2.20"),
            is_active=True
        )
        self.box_flat = ShippingBox.objects.create(
            code="BOX-FLAT",
            name="Flat Mailer Box",
            internal_length=Decimal("38.00"),
            internal_width=Decimal("28.00"),
            internal_height=Decimal("8.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("1.80"),
            is_active=True
        )
        self.box_large = ShippingBox.objects.create(
            code="BOX-L",
            name="Large Shipping Box",
            internal_length=Decimal("45.00"),
            internal_width=Decimal("35.00"),
            internal_height=Decimal("25.00"),
            max_weight=Decimal("15.000"),
            cost=Decimal("3.75"),
            is_active=True
        )
        self.box_heavy = ShippingBox.objects.create(
            code="BOX-XL-HD",
            name="Heavy Duty Freight Box",
            internal_length=Decimal("60.00"),
            internal_width=Decimal("45.00"),
            internal_height=Decimal("35.00"),
            max_weight=Decimal("30.000"),
            cost=Decimal("6.50"),
            is_active=True
        )

        # Standard catalog products
        self.prod_book = Product.objects.create(
            sku="BOOK-DJANGO",
            name="Django for Professionals",
            length=Decimal("23.00"),
            width=Decimal("18.00"),
            height=Decimal("3.50"),
            weight=Decimal("1.100"),
            is_active=True
        )
        self.prod_mug = Product.objects.create(
            sku="MUG-DEV",
            name="Programmer Coffee Mug",
            length=Decimal("11.00"),
            width=Decimal("11.00"),
            height=Decimal("11.00"),
            weight=Decimal("0.380"),
            is_active=True
        )
        self.prod_keyboard = Product.objects.create(
            sku="KEY-MECH",
            name="Mechanical Keyboard",
            length=Decimal("36.00"),
            width=Decimal("14.00"),
            height=Decimal("4.50"),
            weight=Decimal("0.950"),
            is_active=True
        )

    # =========================================================================
    # Category 1: Product Model Validation
    # =========================================================================
    def test_category_01_product_model_validation(self):
        """Verifies valid creation, volume calculation, and SKU uniqueness."""
        prod = Product(
            sku="PROD-VALID-01",
            name="Wireless Mouse",
            length=Decimal("12.00"),
            width=Decimal("7.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.120")
        )
        # clean() must succeed without raising ValidationError
        prod.full_clean()
        prod.save()

        # Volume calculation check: 12 * 7 * 4 = 336.00 cm³
        self.assertEqual(prod.volume, Decimal("336.00"))
        # Sorted dimensions helper check: (min, mid, max)
        self.assertEqual(prod.sorted_dimensions, (Decimal("4.00"), Decimal("7.00"), Decimal("12.00")))

        # Duplicate SKU must raise IntegrityError
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                sku="PROD-VALID-01",
                name="Duplicate SKU Mouse",
                length=Decimal("10.00"),
                width=Decimal("5.00"),
                height=Decimal("2.00"),
                weight=Decimal("0.100")
            )

    # =========================================================================
    # Category 2: Shipping Box Model Validation
    # =========================================================================
    def test_category_02_shipping_box_model_validation(self):
        """Verifies box creation, volume calculation, and code uniqueness."""
        box = ShippingBox(
            code="BOX-CUSTOM-01",
            name="Custom Electronics Shipper",
            internal_length=Decimal("20.00"),
            internal_width=Decimal("20.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("6.000"),
            cost=Decimal("2.10")
        )
        box.full_clean()
        box.save()

        # Volume: 20 * 20 * 10 = 4000.00 cm³
        self.assertEqual(box.internal_volume, Decimal("4000.00"))
        self.assertEqual(box.sorted_dimensions, (Decimal("10.00"), Decimal("20.00"), Decimal("20.00")))

        # Duplicate Box code must raise IntegrityError
        with self.assertRaises(IntegrityError):
            ShippingBox.objects.create(
                code="BOX-CUSTOM-01",
                name="Duplicate Code Box",
                internal_length=Decimal("15.00"),
                internal_width=Decimal("15.00"),
                internal_height=Decimal("15.00"),
                max_weight=Decimal("5.000"),
                cost=Decimal("1.50")
            )

    # =========================================================================
    # Category 3: Order and OrderItem Relationships
    # =========================================================================
    def test_category_03_order_and_orderitem_relationships(self):
        """Verifies FK cascades, reverse lookup, and protection from deletion."""
        order = Order.objects.create()
        item1 = OrderItem.objects.create(
            order=order,
            product=self.prod_book,
            quantity=2,
            unit_weight=self.prod_book.weight
        )
        item2 = OrderItem.objects.create(
            order=order,
            product=self.prod_mug,
            quantity=1,
            unit_weight=self.prod_mug.weight
        )

        # Reverse lookup via related_name='items'
        self.assertEqual(order.items.count(), 2)
        self.assertIn(item1, order.items.all())
        self.assertIn(item2, order.items.all())

        # Duplicate product in same order must violate UniqueConstraint(order, product)
        # We wrap in transaction.atomic() to create a savepoint so SQLite transaction remains healthy
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrderItem.objects.create(
                    order=order,
                    product=self.prod_book,
                    quantity=1,
                    unit_weight=self.prod_book.weight
                )

        # Product referenced in active order item must be PROTECTED from accidental deletion
        with self.assertRaises(ProtectedError):
            self.prod_book.delete()

    # =========================================================================
    # Category 4: Total Order Weight Calculation
    # =========================================================================
    def test_category_04_total_order_weight_calculation(self):
        """Verifies correct calculation of order total weight and volume."""
        order = Order.objects.create()
        # 3 books @ 1.100 kg = 3.300 kg
        OrderItem.objects.create(
            order=order,
            product=self.prod_book,
            quantity=3,
            unit_weight=self.prod_book.weight
        )
        # 2 mugs @ 0.380 kg = 0.760 kg
        OrderItem.objects.create(
            order=order,
            product=self.prod_mug,
            quantity=2,
            unit_weight=self.prod_mug.weight
        )

        order.update_totals_from_items()
        order.save()

        # Expected weight: 3.300 + 0.760 = 4.060 kg
        self.assertEqual(order.total_weight, Decimal("4.060"))

        # Expected volume: 3 * (23 * 18 * 3.5 = 1449) + 2 * (11 * 11 * 11 = 1331)
        # = 3 * 1449 + 2 * 1331 = 4347 + 2662 = 7009.00 cm³
        self.assertEqual(order.total_volume, Decimal("7009.00"))

    # =========================================================================
    # Category 5: Product Dimensional Feasibility (Volume vs Geometry)
    # =========================================================================
    def test_category_05_product_dimensional_feasibility(self):
        """
        Verifies that total volume feasibility alone does NOT guarantee physical fit.
        A long thin item (fluorescent tube / curtain rod) has very small volume,
        yet physically cannot fit into a box whose length is shorter than the item.
        """
        # Pole: 40 cm long, 3 cm wide, 3 cm high. Volume = 360 cm³. Weight = 0.5 kg
        # Box Small: 22 x 16 x 10 cm. Volume = 3520 cm³ (nearly 10x the item volume!)
        # Despite volume passing, the 40 cm pole cannot physically fit in 22 cm length.
        pole = ItemCuboid(
            sku="POLE-40",
            length=Decimal("40.00"),
            width=Decimal("3.00"),
            height=Decimal("3.00"),
            weight=Decimal("0.500")
        )

        # Test against small box directly with 3D engine
        small_box_spec = BoxSpec(
            name=self.box_small.name,
            code=self.box_small.code,
            length=self.box_small.internal_length,
            width=self.box_small.internal_width,
            height=self.box_small.internal_height,
            max_weight=self.box_small.max_weight,
            cost=self.box_small.cost
        )
        fit_result = PackingEngine.can_pack(small_box_spec, [pole])
        self.assertFalse(fit_result.is_fit, "Engine must not fit a 40cm pole into a 22cm box!")

        # Now test against entire catalog:
        # Box Flat has length 38 cm (still too small for 40 cm).
        # Box Medium has length 32 cm (still too small).
        # Box Large has length 45 cm, width 35 cm, height 25 cm -> fits!
        result = BoxSelectorService.select_box_for_items([(pole, 1)])
        self.assertTrue(result.is_success)
        self.assertEqual(result.recommended_box.code, "BOX-L")

    # =========================================================================
    # Category 6: Product Rotation in 3D Space
    # =========================================================================
    def test_category_06_product_rotation(self):
        """
        Verifies that the packing engine evaluates all 6 orthogonal spatial rotations
        (XYZ permutations) and successfully fits items whose initial orientation
        does not match the carton dimensions.
        """
        # Box Medium: 32 (L) x 24 (W) x 16 (H)
        # Product default dimensions: 15 (L) x 28 (W) x 12 (H)
        # Naive orientation fails because W=28 > Box W=24.
        # But rotated to 28 (L) x 15 (W) x 12 (H):
        # 28 <= 32, 15 <= 24, 12 <= 16 -> FITS!
        wide_item = ItemCuboid(
            sku="WIDE-BOARD",
            length=Decimal("15.00"),
            width=Decimal("28.00"),
            height=Decimal("12.00"),
            weight=Decimal("1.500")
        )

        med_spec = BoxSpec(
            name=self.box_medium.name,
            code=self.box_medium.code,
            length=self.box_medium.internal_length,
            width=self.box_medium.internal_width,
            height=self.box_medium.internal_height,
            max_weight=self.box_medium.max_weight,
            cost=self.box_medium.cost
        )

        pack_res = PackingEngine.can_pack(med_spec, [wide_item])
        self.assertTrue(pack_res.is_fit, "Rotated item must fit inside Medium Box.")
        placed = pack_res.placed_items[0]
        self.assertLessEqual(placed.x2, med_spec.length)
        self.assertLessEqual(placed.y2, med_spec.width)
        self.assertLessEqual(placed.z2, med_spec.height)

    # =========================================================================
    # Category 7: Multiple Products Packed Simultaneously
    # =========================================================================
    def test_category_07_multiple_products(self):
        """
        Verifies collision-free placement and boundary adherence for a heterogeneous order:
        1 book (23x18x3.5) + 1 coffee mug (11x11x11) + 1 keyboard (36x14x4.5).
        """
        item_book = ItemCuboid(
            sku=self.prod_book.sku,
            length=self.prod_book.length,
            width=self.prod_book.width,
            height=self.prod_book.height,
            weight=self.prod_book.weight
        )
        item_mug = ItemCuboid(
            sku=self.prod_mug.sku,
            length=self.prod_mug.length,
            width=self.prod_mug.width,
            height=self.prod_mug.height,
            weight=self.prod_mug.weight
        )
        item_key = ItemCuboid(
            sku=self.prod_keyboard.sku,
            length=self.prod_keyboard.length,
            width=self.prod_keyboard.width,
            height=self.prod_keyboard.height,
            weight=self.prod_keyboard.weight
        )

        order_input = [(item_book, 1), (item_mug, 1), (item_key, 1)]
        result = BoxSelectorService.select_box_for_items(order_input)

        self.assertTrue(result.is_success)
        self.assertIsNotNone(result.recommended_box)

        # Verify no 3D overlaps between any pair of placed items
        placed = result.fit_details.placed_items
        self.assertEqual(len(placed), 3)
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                self.assertFalse(
                    PackingEngine.cuboids_overlap(placed[i], placed[j]),
                    f"Items {placed[i].sku} and {placed[j].sku} must not overlap!"
                )

    # =========================================================================
    # Category 8: Multiple Quantities of the Same Product
    # =========================================================================
    def test_category_08_multiple_quantities_of_same_product(self):
        """
        Verifies that an order with quantity > 1 (e.g. 4 coffee mugs)
        unpacks all 4 items, tracks cumulative weight, and packs them with 0 collisions.
        """
        item_mug = ItemCuboid(
            sku=self.prod_mug.sku,
            length=self.prod_mug.length,
            width=self.prod_mug.width,
            height=self.prod_mug.height,
            weight=self.prod_mug.weight
        )

        # 4 mugs: total weight = 4 * 0.380 = 1.520 kg
        result = BoxSelectorService.select_box_for_items([(item_mug, 4)])

        self.assertTrue(result.is_success)
        self.assertEqual(result.total_product_weight, Decimal("1.520"))
        self.assertEqual(len(result.fit_details.placed_items), 4)

        # Verify all 4 mugs are placed inside box boundaries
        box = result.recommended_box
        for p in result.fit_details.placed_items:
            self.assertLessEqual(p.x2, box.internal_length)
            self.assertLessEqual(p.y2, box.internal_width)
            self.assertLessEqual(p.z2, box.internal_height)

    # =========================================================================
    # Category 9: Weight Capacity Exceeded
    # =========================================================================
    def test_category_09_weight_capacity_exceeded(self):
        """
        Verifies that a box is rejected when the order weight exceeds the box's
        max_weight capacity, even if the items easily fit dimensionally.
        """
        # Dense iron weight: 15 x 10 x 5 cm (small volume: 750 cm³), but weight = 4.500 kg
        # Box Small: 22 x 16 x 10 cm, max_weight = 3.000 kg.
        # Fits dimensionally in Box Small, but 4.5 kg > 3.0 kg capacity.
        # Must skip Box Small and choose Box Flat (max 5 kg) or Box Medium (max 8 kg).
        lead_block = ItemCuboid(
            sku="LEAD-4.5KG",
            length=Decimal("15.00"),
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            weight=Decimal("4.500")
        )

        result = BoxSelectorService.select_box_for_items([(lead_block, 1)])
        self.assertTrue(result.is_success)
        self.assertNotEqual(result.recommended_box.code, "BOX-S", "Box Small must be rejected on weight limit!")
        self.assertGreaterEqual(result.recommended_box.max_weight, Decimal("4.500"))

    # =========================================================================
    # Category 10: No Suitable Box Available
    # =========================================================================
    def test_category_10_no_suitable_box_available(self):
        """
        Verifies that when no warehouse box can accommodate the order,
        the service returns UNPACKABLE status and a helpful diagnostic message.
        """
        # 10 huge steel crates: 50 x 40 x 30 cm, weight 10 kg each (Total: 100 kg)
        # Even the largest box (BOX-XL-HD) holds max 30 kg.
        giant_crate = ItemCuboid(
            sku="CRATE-GIANT",
            length=Decimal("50.00"),
            width=Decimal("40.00"),
            height=Decimal("30.00"),
            weight=Decimal("10.000")
        )

        result = BoxSelectorService.select_box_for_items([(giant_crate, 10)])

        self.assertFalse(result.is_success)
        self.assertEqual(result.status, OrderStatus.UNPACKABLE)
        self.assertIsNone(result.recommended_box)
        self.assertIn("Weight Capacity Exceeded", result.reason)

    # =========================================================================
    # Category 11: Empty Order
    # =========================================================================
    def test_category_11_empty_order(self):
        """
        Verifies that an empty order input returns UNPACKABLE without crashing
        or raising unhandled exceptions.
        """
        result = BoxSelectorService.select_box_for_items([])

        self.assertFalse(result.is_success)
        self.assertEqual(result.status, OrderStatus.UNPACKABLE)
        self.assertIsNone(result.recommended_box)
        self.assertIn("contains no items", result.reason)

    # =========================================================================
    # Category 12: Invalid Dimensions (Zero Values)
    # =========================================================================
    def test_category_12_invalid_dimensions(self):
        """
        Verifies that products with 0 length, width, or height are rejected
        both at the model validation level and at the service layer.
        """
        # Model-level validation check
        zero_dim_prod = Product(
            sku="ZERO-DIM",
            name="Flat Paper Plane",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("0.00"),  # Invalid zero height
            weight=Decimal("0.050")
        )
        with self.assertRaises(ValidationError) as ctx:
            zero_dim_prod.clean()
        self.assertIn("height", ctx.exception.message_dict)

        # Service-layer check
        zero_cuboid = ItemCuboid(
            sku="ZERO-DIM",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("0.00"),
            weight=Decimal("0.050")
        )
        res = BoxSelectorService.select_box_for_items([(zero_cuboid, 1)])
        self.assertFalse(res.is_success)
        self.assertEqual(res.status, OrderStatus.UNPACKABLE)
        self.assertIn("Invalid item dimensions", res.reason)

    # =========================================================================
    # Category 13: Zero or Negative Values
    # =========================================================================
    def test_category_13_zero_or_negative_values(self):
        """
        Verifies rejection of negative dimensions, zero weights, and negative box costs.
        """
        # 1. Product with negative dimension
        neg_dim_prod = Product(
            sku="NEG-DIM",
            name="Negative Dimension",
            length=Decimal("-10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        with self.assertRaises(ValidationError):
            neg_dim_prod.clean()

        # 2. Product with zero weight
        zero_wt_prod = Product(
            sku="ZERO-WT",
            name="Weightless Ghost",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.000")
        )
        with self.assertRaises(ValidationError):
            zero_wt_prod.clean()

        # 3. Box with negative cost
        neg_cost_box = ShippingBox(
            code="BOX-NEG-COST",
            name="Subsidized Box",
            internal_length=Decimal("20.00"),
            internal_width=Decimal("20.00"),
            internal_height=Decimal("20.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("-2.50")
        )
        with self.assertRaises(ValidationError):
            neg_cost_box.clean()

        # 4. Service layer rejects negative quantity
        valid_item = ItemCuboid(
            sku="ITEM-OK",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        qty_res = BoxSelectorService.select_box_for_items([(valid_item, -1)])
        self.assertFalse(qty_res.is_success)
        self.assertIn("Must be at least 1", qty_res.reason)

    # =========================================================================
    # Category 14: Multiple Eligible Boxes with Different Costs
    # =========================================================================
    def test_category_14_multiple_eligible_boxes_different_costs(self):
        """
        Verifies that when multiple boxes can accommodate an order,
        the system selects the lowest-cost option (e.g. ₹1.80 vs ₹2.20 vs ₹3.75).
        """
        # 1 Book (23 x 18 x 3.5 cm, 1.100 kg)
        # Box Small (22 x 16 x 10) -> too small in length (22 < 23)
        # Eligible candidates that fit:
        #   - Box Flat (38 x 28 x 8 cm, max 5 kg)  -> Cost: ₹1.80
        #   - Box Medium (32 x 24 x 16 cm, max 8 kg) -> Cost: ₹2.20
        #   - Box Large (45 x 35 x 25 cm, max 15 kg) -> Cost: ₹3.75
        # The algorithm MUST choose Box Flat because ₹1.80 is the minimum cost.
        item_book = ItemCuboid(
            sku=self.prod_book.sku,
            length=self.prod_book.length,
            width=self.prod_book.width,
            height=self.prod_book.height,
            weight=self.prod_book.weight
        )

        result = BoxSelectorService.select_box_for_items([(item_book, 1)])

        self.assertTrue(result.is_success)
        self.assertEqual(
            result.recommended_box.code,
            "BOX-FLAT",
            f"Expected lowest-cost BOX-FLAT (₹1.80), but got {result.recommended_box.code} (₹{result.box_cost})"
        )
        self.assertEqual(result.box_cost, Decimal("1.80"))

    # =========================================================================
    # Category 15: Orders Containing Oversized Products
    # =========================================================================
    def test_category_15_orders_containing_oversized_products(self):
        """
        Verifies handling of an oversized product whose single dimension
        exceeds the maximum dimension of ANY box in the warehouse.
        E.g., Cross-Country Skis: length 180 cm (largest warehouse box length is 60 cm).
        """
        skis = ItemCuboid(
            sku="SKIS-180CM",
            length=Decimal("180.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            weight=Decimal("3.500")
        )

        result = BoxSelectorService.select_box_for_items([(skis, 1)])

        self.assertFalse(result.is_success)
        self.assertEqual(result.status, OrderStatus.UNPACKABLE)
        self.assertIsNone(result.recommended_box)
        # Verify diagnosis explicitly identifies the oversized SKU
        self.assertIn("Oversized Item", result.reason)
        self.assertIn("SKIS-180CM", result.reason)
