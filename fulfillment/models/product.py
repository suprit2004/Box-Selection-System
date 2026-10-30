from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Product(models.Model):
    """
    Represents an item available in the ecommerce catalog that requires shipping.
    """
    sku = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Unique Stock Keeping Unit (e.g., 'PROD-BOOK-001')"
    )
    name = models.CharField(max_length=255)

    # Physical dimensions in centimeters (cm)
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Length in cm (minimum 0.01)"
    )
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width in cm (minimum 0.01)"
    )
    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height in cm (minimum 0.01)"
    )

    # Physical weight in kilograms (kg)
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Weight in kg (minimum 0.001)"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates whether this product is eligible for active orders."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(length__gt=0) &
                models.Q(width__gt=0) &
                models.Q(height__gt=0) &
                models.Q(weight__gt=0),
                name='product_positive_dimensions_and_weight'
            )
        ]

    def clean(self):
        super().clean()
        if self.length is not None and self.length <= 0:
            raise ValidationError({'length': "Product length must be strictly positive."})
        if self.width is not None and self.width <= 0:
            raise ValidationError({'width': "Product width must be strictly positive."})
        if self.height is not None and self.height <= 0:
            raise ValidationError({'height': "Product height must be strictly positive."})
        if self.weight is not None and self.weight <= 0:
            raise ValidationError({'weight': "Product weight must be strictly positive."})

    @property
    def volume(self) -> Decimal:
        """Returns product volume in cm³."""
        return self.length * self.width * self.height

    @property
    def sorted_dimensions(self) -> tuple[Decimal, Decimal, Decimal]:
        """Returns (min, mid, max) dimensions for rotation-invariant checks."""
        return tuple(sorted([self.length, self.width, self.height]))

    def __str__(self):
        return f"{self.name} ({self.sku})"

