# Generated by Django 5.1.1 on 2024-10-01 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0002_order_delivery"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="deliveryoptions",
            options={"ordering": ["price"]},
        ),
    ]
