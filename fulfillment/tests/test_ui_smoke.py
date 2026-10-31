"""
Full-page integration smoke-test that renders every template via Django test client
to catch any template syntax errors, missing context variables, or broken URL tags.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from fulfillment.models import Product, ShippingBox, Order, OrderItem, OrderStatus


class FullPageSmokeTest(TestCase):
    """Renders every page end-to-end to detect template errors."""

    def setUp(self):
        self.client = Client()
        self.box = ShippingBox.objects.create(
            code="BOX-SMOKE",
            name="Smoke Test Box",
            internal_length=Decimal("40.00"),
            internal_width=Decimal("30.00"),
            internal_height=Decimal("20.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("3.00")
        )
        self.product = Product.objects.create(
            sku="SMOKE-01",
            name="Smoke Test Book",
            length=Decimal("20.00"),
            width=Decimal("14.00"),
            height=Decimal("3.00"),
            weight=Decimal("0.800")
        )
        self.order = Order.objects.create(
            status=OrderStatus.OPTIMIZED,
            recommended_box=self.box,
            total_weight=Decimal("0.800"),
            total_volume=Decimal("840.00"),
            packing_notes="Selected Smoke Test Box as the cheapest feasible box."
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_weight=self.product.weight
        )
        self.unpackable_order = Order.objects.create(
            status=OrderStatus.UNPACKABLE,
            recommended_box=None,
            total_weight=Decimal("999.00"),
            total_volume=Decimal("0.00"),
            packing_notes="Weight Capacity Exceeded."
        )

    # 1. Dashboard
    def test_dashboard_renders(self):
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Warehouse Packaging Dashboard")
        self.assertContains(r, "Catalog Products")
        self.assertContains(r, "Shipping Boxes")
        self.assertContains(r, "Total Orders")
        self.assertContains(r, "Fit Success Rate")
        self.assertContains(r, "Smoke Test Box")

    # 2. Products list + form
    def test_product_list_renders(self):
        r = self.client.get(reverse('product_list_create'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Product Catalog")
        self.assertContains(r, "Smoke Test Book")
        self.assertContains(r, "Add New Product")

    # 3. Product edit
    def test_product_edit_renders(self):
        r = self.client.get(reverse('product_edit', args=[self.product.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Edit Product")
        self.assertContains(r, "SMOKE-01")

    # 4. Product delete confirmation
    def test_product_delete_confirm_renders(self):
        r = self.client.get(reverse('product_delete', args=[self.product.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Confirm Product Deletion")
        self.assertContains(r, "Yes, Delete Permanently")
        self.assertContains(r, "Cancel")

    # 5. Boxes list + form
    def test_box_list_renders(self):
        r = self.client.get(reverse('box_list_create'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Shipping Box Inventory")
        self.assertContains(r, "Smoke Test Box")
        self.assertContains(r, "Add Shipping Box")

    # 6. Box edit
    def test_box_edit_renders(self):
        r = self.client.get(reverse('box_edit', args=[self.box.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Edit Shipping Box")
        self.assertContains(r, "BOX-SMOKE")

    # 7. Box delete confirmation
    def test_box_delete_confirm_renders(self):
        r = self.client.get(reverse('box_delete', args=[self.box.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Confirm Shipping Box Deletion")

    # 8. Create order form
    def test_order_create_renders(self):
        r = self.client.get(reverse('order_create'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Create Fulfillment Order")
        self.assertContains(r, "Smoke Test Book")
        self.assertContains(r, "Optimize")

    # 9. Recommendation page — OPTIMIZED
    def test_recommendation_optimized_renders(self):
        r = self.client.get(reverse('order_recommendation', args=[self.order.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Box Recommended")
        self.assertContains(r, "Smoke Test Box")
        self.assertContains(r, "₹3.00")
        self.assertContains(r, "Reason for Selection")
        self.assertContains(r, "3D Coordinate Placement")

    # 10. Recommendation page — UNPACKABLE
    def test_recommendation_unpackable_renders(self):
        r = self.client.get(reverse('order_recommendation', args=[self.unpackable_order.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "No Box Accommodates Order")
        self.assertContains(r, "No Suitable Shipping Box in Stock")

    # 11. Orders history list
    def test_order_list_renders(self):
        r = self.client.get(reverse('order_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Orders")
        self.assertContains(r, self.order.order_number)
        self.assertContains(r, "Box Selected")
        self.assertContains(r, "Unpackable")

    # 12. Navbar active highlighting (base template rendered correctly)
    def test_navbar_present_on_all_key_pages(self):
        urls = ['dashboard', 'product_list_create', 'box_list_create', 'order_list', 'order_create']
        for url_name in urls:
            r = self.client.get(reverse(url_name))
            self.assertEqual(r.status_code, 200, msg=f"Page '{url_name}' returned {r.status_code}")
            self.assertContains(r, "Box Selection System", msg_prefix=f"Navbar missing on {url_name}")

