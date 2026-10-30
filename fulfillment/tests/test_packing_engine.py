from decimal import Decimal
from django.test import SimpleTestCase
from fulfillment.services.packing_engine import PackingEngine, BoxSpec, ItemCuboid, PlacedCuboid


class PackingEngineTest(SimpleTestCase):
    def setUp(self):
        self.standard_box = BoxSpec(
            name="Standard Box",
            code="BOX-STD",
            length=Decimal("30.00"),
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("2.50")
        )

    def test_single_item_fits_without_rotation(self):
        item = ItemCuboid(
            sku="ITEM-1",
            length=Decimal("20.00"),
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            weight=Decimal("1.000")
        )
        result = PackingEngine.can_pack(self.standard_box, [item])
        self.assertTrue(result.is_fit)
        self.assertEqual(len(result.placed_items), 1)
        self.assertEqual(result.placed_items[0].sku, "ITEM-1")

    def test_item_fits_only_with_3d_rotation(self):
        # Box is 30 x 20 x 15
        # Item is 18 x 25 x 10 -> (18 > 15, 25 > 20) in naive orientation
        # If rotated so length=25, width=18, height=10 -> fits inside 30 x 20 x 15!
        item = ItemCuboid(
            sku="ROTATED-ITEM",
            length=Decimal("18.00"),
            width=Decimal("25.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        result = PackingEngine.can_pack(self.standard_box, [item])
        self.assertTrue(result.is_fit)
        self.assertEqual(len(result.placed_items), 1)
        placed = result.placed_items[0]
        self.assertLessEqual(placed.x2, self.standard_box.length)
        self.assertLessEqual(placed.y2, self.standard_box.width)
        self.assertLessEqual(placed.z2, self.standard_box.height)

    def test_fluorescent_tube_volume_trap_fails(self):
        # Item has small volume (50 * 2 * 2 = 200 cm³), well under box volume (9000 cm³),
        # but length 50 cm exceeds box length 30 cm in any rotation!
        tube = ItemCuboid(
            sku="TUBE-01",
            length=Decimal("50.00"),
            width=Decimal("2.00"),
            height=Decimal("2.00"),
            weight=Decimal("0.500")
        )
        result = PackingEngine.can_pack(self.standard_box, [tube])
        self.assertFalse(result.is_fit)
        self.assertEqual(len(result.unfitted_items), 1)

    def test_multi_item_packing_success(self):
        # Two identical boxes of 12 x 18 x 6 cm into 30 x 20 x 15 cm
        item1 = ItemCuboid(sku="CUBE-1", length=Decimal("12.00"), width=Decimal("18.00"), height=Decimal("6.00"), weight=Decimal("1.000"))
        item2 = ItemCuboid(sku="CUBE-2", length=Decimal("12.00"), width=Decimal("18.00"), height=Decimal("6.00"), weight=Decimal("1.000"))

        result = PackingEngine.can_pack(self.standard_box, [item1, item2])
        self.assertTrue(result.is_fit)
        self.assertEqual(len(result.placed_items), 2)
        # Check no overlap between placed items
        self.assertFalse(PackingEngine.cuboids_overlap(result.placed_items[0], result.placed_items[1]))

    def test_cuboids_touching_faces_do_not_overlap(self):
        c1 = PlacedCuboid(sku="A", x=Decimal("0"), y=Decimal("0"), z=Decimal("0"), dx=Decimal("10"), dy=Decimal("10"), dz=Decimal("10"))
        # c2 placed immediately adjacent to c1 on X axis (x starts at 10)
        c2 = PlacedCuboid(sku="B", x=Decimal("10"), y=Decimal("0"), z=Decimal("0"), dx=Decimal("10"), dy=Decimal("10"), dz=Decimal("10"))
        self.assertFalse(PackingEngine.cuboids_overlap(c1, c2))

