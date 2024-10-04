from account.models import Customer
from coupon.models import Coupon
from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from shop.models import Product


class DeliveryOptions(models.Model):
    EXPRESS = "express"
    STANDARD = "standard"
    SAME_DAY = "same_day"
    DELIVERY_OPTIONS = [
        (STANDARD, "Standard"),
        (EXPRESS, "Express"),
        (SAME_DAY, "Same_day"),
    ]

    delivery_type = models.CharField(max_length=30, choices=DELIVERY_OPTIONS)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deliverd_time = models.CharField(max_length=50, help_text="how many days/weeks takes thise delivery option")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return self.delivery_type


class Order(models.Model):
    PENDING = "pending"
    SHIPPING = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"

    ORDER_STATUS = [
        (PENDING, "Pending"),
        (SHIPPING, "Shipped"),
        (DELIVERED, "Delivered"),
        (CANCELED, "Canceled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="orders", null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, related_name="orders", blank=True, null=True)
    delivery = models.ForeignKey(
        DeliveryOptions,
        on_delete=models.RESTRICT,
        related_name="orders",
        null=True,
        blank=True,
    )

    fullname = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(8), MaxLengthValidator(15)],
        help_text="phone number length must be between 8 - 15",
    )

    postal_code = models.IntegerField(
        verbose_name="Postal Code",
        validators=[MinValueValidator(100000)],
        help_text="postal code should have more than 5 digits",
    )

    state = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=255, verbose_name="Address first line")
    address_line_2 = models.CharField(max_length=255, verbose_name="Address second line", blank=True, null=True)

    order_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    pay_status = models.BooleanField(default=False)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "pay_status")
        indexes = [models.Index(fields=["customer", "created_at"])]

    def apply_delivery(self, delivery_option):
        self.delivery = delivery_option
        self.delivery_price = delivery_option.price
        self.save()

    def apply_coupon(self, coupon):
        self.coupon = coupon
        self.discount_amount = coupon.calculate_discount(self.order_price)
        self.save()

    @property
    def total_price(self):
        return self.payments.total_price
        # if self.coupon:
        # return self.order_price - self.discount_amount
        # return self.order_price

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderitems")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orderitems")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=["order"])]

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (order {self.order.id})"


class PaymentDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payments", null=True)
    platform_provider = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment Detail"
        verbose_name_plural = "Payment Details"

    def __str__(self):
        return f"Payment {self.payment_id} - {self.platform_provider}"
