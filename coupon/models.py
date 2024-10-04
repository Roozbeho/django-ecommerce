from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [("percentage", "Percentage"), ("fixed", "Fixed")]

    code = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(4)],
        unique=True,
        verbose_name="Coupon Name",
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default="percentage",
        help_text="Type Of Coupun, percentage or fixed amount",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="percatage type should be between 1 and 100, and fixed amount max length is 10",
    )
    max_uses = models.PositiveIntegerField(
        verbose_name="Max Uses", help_text="Maximum number of uses this coupon allows"
    )
    max_uses_per_user = models.PositiveIntegerField(help_text="How many times users can use this coupon")
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Min price of a product that is valid for this coupon",
    )
    description = models.CharField(max_length=500, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["valid_from", "valid_to"]),
        ]

    def is_valid(self, price):
        # from decimal import Decimal

        now = timezone.now()
        print(price > self.min_price, "by" * 10)
        return now <= self.valid_to and now >= self.valid_from and self.is_active and price > self.min_price

    def clean(self):
        # print(self.discount_type, '5'*40)
        if self.discount_type == "percentage":
            if self.discount_amount > 100 or self.discount_amount < 0:
                raise ValidationError("percentage must be between 0 and 100")

    def calculate_discount(self, price):
        print(self.discount_type, "5" * 40)
        if self.discount_type == "percentage":
            return price * (self.discount_amount / 100)
        return self.discount_amount

    def __str__(self):
        return self.code
