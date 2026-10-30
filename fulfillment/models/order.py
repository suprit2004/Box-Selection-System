from decimal import Decimal
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .box import ShippingBox
from .product import Product


class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Recommendation'
    OPTIMIZED = 'OPTIMIZED', 'Box Selected'
    UNPACKABLE = 'UNPACKABLE', 'No Box Accommodates Order'


def generate_order_number() -> str:
    """Generates a concise, unique order identifier, e.g. ORD-A1B2C3D4"""
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


class Order(models.Model):
    """
    Represents an incoming customer order requiring packaging optimization.
    """
    order_number = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        default=generate_order_number,
        help_text="Unique customer order reference"
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True
    )
    recommended_box = models.ForeignKey(
        ShippingBox,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
        help_text="The optimal shipping box selected by the packing engine."
    )
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        help_text="Calculated total weight of all products in kg"
    )
    total_volume = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated total volume of all products in cm³"
    )
    packing_notes = models.TextField(
        blank=True,
        help_text="Diagnostic reasoning or warehouse packing notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def update_totals_from_items(self):
        """Calculates and updates total weight and volume based on current order items."""
        total_w = Decimal('0.000')
        total_v = Decimal('0.00')
        for item in self.items.select_related('product').all():
            total_w += item.unit_weight * item.quantity
            total_v += item.product.volume * item.quantity
        self.total_weight = total_w
        self.total_volume = total_v

    def __str__(self):
        return f"{self.order_number} ({self.get_status_display()})"


class OrderItem(models.Model):
    """
    Line item linking a Product to an Order with a specific ordered quantity.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity of this product in the order (minimum 1)"
    )
    unit_weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        help_text="Snapshot of the unit weight at the time the order was placed"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_product_per_order'
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='item_quantity_minimum_one'
            )
        ]

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity < 1:
            raise ValidationError({'quantity': "Item quantity must be at least 1."})

    def save(self, *args, **kwargs):
        if not self.unit_weight and self.product_id:
            self.unit_weight = self.product.weight
        super().save(*args, **kwargs)

    @property
    def line_weight(self) -> Decimal:
        return self.unit_weight * self.quantity

    @property
    def line_volume(self) -> Decimal:
        return self.product.volume * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

