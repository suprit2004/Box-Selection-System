from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from fulfillment.models import Product, ShippingBox, Order, OrderItem, OrderStatus


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.box = ShippingBox.objects.create(
            code="BOX-STD",
            name="Standard Box",
            internal_length=Decimal("30.00"),
            internal_width=Decimal("20.00"),
            internal_height=Decimal("15.00"),
            max_weight=Decimal("10.000"),
            cost=Decimal("2.50")
        )
        self.product = Product.objects.create(
            sku="BOOK-01",
            name="Django for Professionals",
            length=Decimal("22.00"),
            width=Decimal("16.00"),
            height=Decimal("3.00"),
            weight=Decimal("0.900")
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Warehouse Packaging Dashboard")
        self.assertContains(response, "Catalog Products")
        self.assertContains(response, "Shipping Boxes")

    def test_home_page_renders_dashboard(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Warehouse Packaging Dashboard")

    def test_product_delete_confirmation_page(self):
        temp = Product.objects.create(
            sku="TEMP-02", name="Temp Product",
            length=Decimal("5.00"), width=Decimal("5.00"),
            height=Decimal("5.00"), weight=Decimal("0.500")
        )
        response = self.client.get(reverse('product_delete', args=[temp.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Product Deletion")
        self.assertContains(response, "TEMP-02")

    def test_box_delete_confirmation_page(self):
        temp_box = ShippingBox.objects.create(
            code="BOX-DEL-TMP", name="Delete Test Box",
            internal_length=Decimal("10.00"), internal_width=Decimal("10.00"),
            internal_height=Decimal("10.00"), max_weight=Decimal("2.000"),
            cost=Decimal("0.50")
        )
        response = self.client.get(reverse('box_delete', args=[temp_box.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Shipping Box Deletion")
        self.assertContains(response, "BOX-DEL-TMP")

    def test_product_list_create_get_and_post(self):
        response = self.client.get(reverse('product_list_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django for Professionals")

        post_data = {
            'sku': 'NEW-SKU-99',
            'name': 'Wireless Mouse',
            'length': '12.00',
            'width': '8.00',
            'height': '4.00',
            'weight': '0.150',
            'is_active': 'on'
        }
        post_response = self.client.post(reverse('product_list_create'), post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(Product.objects.filter(sku='NEW-SKU-99').exists())

    def test_product_edit(self):
        response = self.client.get(reverse('product_edit', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Product")

        update_data = {
            'sku': self.product.sku,
            'name': 'Django for Senior Professionals',
            'length': '22.00',
            'width': '16.00',
            'height': '3.50',
            'weight': '0.950',
            'is_active': 'on'
        }
        post_response = self.client.post(reverse('product_edit', args=[self.product.pk]), update_data)
        self.assertEqual(post_response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Django for Senior Professionals')

    def test_product_delete_safe(self):
        # Product not in any order can be deleted cleanly
        temp_product = Product.objects.create(
            sku="TEMP-01",
            name="Temporary Item",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        post_response = self.client.post(reverse('product_delete', args=[temp_product.pk]))
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(Product.objects.filter(sku="TEMP-01").exists())

    def test_product_delete_protected_by_order(self):
        # Product referenced in an order cannot be deleted; protected gracefully
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product, quantity=1, unit_weight=self.product.weight)
        
        post_response = self.client.post(reverse('product_delete', args=[self.product.pk]))
        self.assertEqual(post_response.status_code, 302)
        # Verify product still exists and was not deleted
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_box_list_create_get_and_post(self):
        response = self.client.get(reverse('box_list_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Standard Box")

        post_data = {
            'code': 'BOX-NEW',
            'name': 'New Carton',
            'internal_length': '25.00',
            'internal_width': '15.00',
            'internal_height': '10.00',
            'max_weight': '5.000',
            'cost': '1.75',
            'is_active': 'on'
        }
        post_response = self.client.post(reverse('box_list_create'), post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(ShippingBox.objects.filter(code='BOX-NEW').exists())

    def test_box_edit(self):
        response = self.client.get(reverse('box_edit', args=[self.box.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Shipping Box")

        update_data = {
            'code': self.box.code,
            'name': 'Standard Box Revised',
            'internal_length': '30.00',
            'internal_width': '20.00',
            'internal_height': '15.00',
            'max_weight': '12.000',
            'cost': '2.60',
            'is_active': 'on'
        }
        post_response = self.client.post(reverse('box_edit', args=[self.box.pk]), update_data)
        self.assertEqual(post_response.status_code, 302)
        self.box.refresh_from_db()
        self.assertEqual(self.box.name, 'Standard Box Revised')

    def test_box_delete(self):
        temp_box = ShippingBox.objects.create(
            code="BOX-TEMP",
            name="Temporary Carton",
            internal_length=Decimal("20.00"),
            internal_width=Decimal("15.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("1.00")
        )
        post_response = self.client.post(reverse('box_delete', args=[temp_box.pk]))
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(ShippingBox.objects.filter(code="BOX-TEMP").exists())

    def test_order_create_post_and_recommendation_redirect(self):
        post_data = {
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '1',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product': str(self.product.id),
            'items-0-quantity': '1',
        }
        response = self.client.post(reverse('order_create'), post_data)
        self.assertEqual(response.status_code, 302)

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.OPTIMIZED)
        self.assertEqual(order.recommended_box, self.box)

        rec_response = self.client.get(reverse('order_recommendation', args=[order.id]))
        self.assertEqual(rec_response.status_code, 200)
        self.assertContains(rec_response, "Standard Box")
        self.assertContains(rec_response, "₹2.50")

    def test_order_list_view(self):
        order = Order.objects.create(status=OrderStatus.OPTIMIZED, recommended_box=self.box)
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)

    def test_seed_sample_data_endpoint(self):
        response = self.client.get(reverse('seed_sample_data'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ShippingBox.objects.filter(code='BOX-XL').exists())
        self.assertTrue(Product.objects.filter(sku='PROD-MUG-01').exists())
