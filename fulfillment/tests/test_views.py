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

    def test_home_page_redirect_or_render(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Order & Select Box")

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
        self.assertContains(rec_response, "$2.50")

    def test_seed_sample_data_endpoint(self):
        response = self.client.get(reverse('seed_sample_data'))
        self.assertEqual(response.status_code, 302)
        # Verify sample data populated
        self.assertTrue(ShippingBox.objects.filter(code='BOX-XL').exists())
        self.assertTrue(Product.objects.filter(sku='PROD-MUG-01').exists())

