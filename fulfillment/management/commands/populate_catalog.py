from decimal import Decimal
from django.core.management.base import BaseCommand
from fulfillment.models import Product, ShippingBox


class Command(BaseCommand):
    help = "Populates realistic shipping boxes and catalog products for demonstration."

    def handle(self, *args, **options):
        sample_boxes = [
            {"code": "BOX-S", "name": "Small Parcel Box", "internal_length": Decimal("22.00"), "internal_width": Decimal("16.00"), "internal_height": Decimal("10.00"), "max_weight": Decimal("3.000"), "cost": Decimal("1.25")},
            {"code": "BOX-M", "name": "Medium Shipping Box", "internal_length": Decimal("32.00"), "internal_width": Decimal("24.00"), "internal_height": Decimal("16.00"), "max_weight": Decimal("8.000"), "cost": Decimal("2.20")},
            {"code": "BOX-FLAT", "name": "Flat Mailer Box", "internal_length": Decimal("38.00"), "internal_width": Decimal("28.00"), "internal_height": Decimal("8.00"), "max_weight": Decimal("5.000"), "cost": Decimal("1.80")},
            {"code": "BOX-L", "name": "Large Shipping Box", "internal_length": Decimal("45.00"), "internal_width": Decimal("35.00"), "internal_height": Decimal("25.00"), "max_weight": Decimal("15.000"), "cost": Decimal("3.75")},
            {"code": "BOX-XL", "name": "Heavy Duty Box", "internal_length": Decimal("60.00"), "internal_width": Decimal("45.00"), "internal_height": Decimal("35.00"), "max_weight": Decimal("25.000"), "cost": Decimal("5.50")},
        ]

        sample_products = [
            {"sku": "PROD-BOOK-01", "name": "Hardcover Programming Book", "length": Decimal("24.00"), "width": Decimal("17.00"), "height": Decimal("4.50"), "weight": Decimal("1.100")},
            {"sku": "PROD-MUG-01", "name": "Ceramic Coffee Mug", "length": Decimal("11.00"), "width": Decimal("11.00"), "height": Decimal("11.00"), "weight": Decimal("0.380")},
            {"sku": "PROD-SHOE-01", "name": "Running Shoes (Boxed)", "length": Decimal("32.00"), "width": Decimal("20.00"), "height": Decimal("12.00"), "weight": Decimal("1.250")},
            {"sku": "PROD-LAPTOP-01", "name": "15-inch Laptop", "length": Decimal("36.00"), "width": Decimal("26.00"), "height": Decimal("3.00"), "weight": Decimal("2.200")},
            {"sku": "PROD-ROLLER-01", "name": "Fitness Foam Roller", "length": Decimal("45.00"), "width": Decimal("15.00"), "height": Decimal("15.00"), "weight": Decimal("0.850")},
            {"sku": "PROD-SKI-OVERSIZED", "name": "Cross-Country Skis (Oversized)", "length": Decimal("180.00"), "width": Decimal("15.00"), "height": Decimal("10.00"), "weight": Decimal("3.500")},
        ]

        boxes_count = 0
        for b in sample_boxes:
            _, created = ShippingBox.objects.get_or_create(code=b["code"], defaults=b)
            if created:
                boxes_count += 1

        products_count = 0
        for p in sample_products:
            _, created = Product.objects.get_or_create(sku=p["sku"], defaults=p)
            if created:
                products_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully populated catalog: {boxes_count} new boxes and {products_count} new products created."
        ))

