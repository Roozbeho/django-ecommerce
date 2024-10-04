# Generated by Django 5.1.1 on 2024-09-29 09:15

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("coupon", "0004_remove_coupon_category_remove_coupon_products_and_more"),
        ("shop", "0003_product_shop_produc_slug_76971b_idx"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryOptions",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "delivery_type",
                    models.CharField(
                        choices=[
                            ("standard", "Standard"),
                            ("express", "Express"),
                            ("same_day", "Same_day"),
                        ],
                        max_length=30,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "deliverd_time",
                    models.CharField(
                        help_text="how many days/weeks takes thise delivery option",
                        max_length=50,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["-price"],
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fullname", models.CharField(max_length=100)),
                (
                    "phone_number",
                    models.CharField(
                        help_text="phone number length must be between 8 - 15",
                        max_length=50,
                        validators=[
                            django.core.validators.MinLengthValidator(8),
                            django.core.validators.MaxLengthValidator(15),
                        ],
                    ),
                ),
                (
                    "postal_code",
                    models.IntegerField(
                        help_text="postal code should have more than 5 digits",
                        validators=[django.core.validators.MinValueValidator(100000)],
                        verbose_name="Postal Code",
                    ),
                ),
                ("state", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=50)),
                (
                    "address_line_1",
                    models.CharField(max_length=255, verbose_name="Address first line"),
                ),
                (
                    "address_line_2",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Address second line",
                    ),
                ),
                (
                    "total_price_before_coupon",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "discount_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("pay_status", models.BooleanField(default=False)),
                (
                    "order_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("shipped", "Shipped"),
                            ("delivered", "Delivered"),
                            ("canceled", "Canceled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("update_at", models.DateTimeField(auto_now=True)),
                (
                    "coupon",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="coupon.coupon",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at", "pay_status"),
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orderitems",
                        to="order.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orderitems",
                        to="shop.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PaymentDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("platform_provider", models.CharField(max_length=20)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_id", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="order.order",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment Detail",
                "verbose_name_plural": "Payment Details",
            },
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["customer", "created_at"], name="order_order_custome_a09334_idx"),
        ),
        migrations.AddIndex(
            model_name="orderitem",
            index=models.Index(fields=["order"], name="order_order_order_i_854de1_idx"),
        ),
    ]
