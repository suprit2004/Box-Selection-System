from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class ShippingBox(models.Model):
    """
    Represents an available standard shipping box in the warehouse inventory.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Standard packaging identifier (e.g., 'BOX-S', 'BOX-M', 'BOX-L')"
    )
    name = models.CharField(max_length=100)

    # Internal usable dimensions in centimeters (cm)
    internal_length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal length in cm"
    )
    internal_width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal width in cm"
    )
    internal_height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal height in cm"
    )

    # Maximum carrying capacity in kilograms (kg)
    max_weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Maximum weight capacity in kg"
    )

    # Cost per unit in currency units
    cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost per box"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates whether this box is currently available for packaging."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['cost', 'internal_length']
        verbose_name = "Shipping Box"
        verbose_name_plural = "Shipping Boxes"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(internal_length__gt=0) &
                models.Q(internal_width__gt=0) &
                models.Q(internal_height__gt=0) &
                models.Q(max_weight__gt=0) &
                models.Q(cost__gte=0),
                name='box_positive_attributes'
            )
        ]

    def clean(self):
        super().clean()
        if self.internal_length is not None and self.internal_length <= 0:
            raise ValidationError({'internal_length': "Internal length must be strictly positive."})
        if self.internal_width is not None and self.internal_width <= 0:
            raise ValidationError({'internal_width': "Internal width must be strictly positive."})
        if self.internal_height is not None and self.internal_height <= 0:
            raise ValidationError({'internal_height': "Internal height must be strictly positive."})
        if self.max_weight is not None and self.max_weight <= 0:
            raise ValidationError({'max_weight': "Maximum weight capacity must be strictly positive."})
        if self.cost is not None and self.cost < 0:
            raise ValidationError({'cost': "Box cost cannot be negative."})

    @property
    def internal_volume(self) -> Decimal:
        """Returns internal usable volume in cm³."""
        return self.internal_length * self.internal_width * self.internal_height

    @property
    def sorted_dimensions(self) -> tuple[Decimal, Decimal, Decimal]:
        """Returns (min, mid, max) dimensions for rotation-invariant checks."""
        return tuple(sorted([self.internal_length, self.internal_width, self.internal_height]))

    def __str__(self):
        return f"{self.name} [{self.code}] - ₹{self.cost:.2f}"

