# Generated by Django 5.1.1 on 2024-10-03 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0007_rename_total_price_before_coupon_order_order_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_price",
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10),
        ),
    ]
