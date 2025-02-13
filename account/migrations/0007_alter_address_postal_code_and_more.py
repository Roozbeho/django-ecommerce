# Generated by Django 5.1.1 on 2024-09-28 20:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0006_customer_account_cus_email_32dadd_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="postal_code",
            field=models.IntegerField(
                help_text="postal code should have more than 5 digits",
                validators=[django.core.validators.MinValueValidator(100000)],
                verbose_name="Postal Code",
            ),
        ),
        migrations.AddIndex(
            model_name="address",
            index=models.Index(fields=["id"], name="account_add_id_b09351_idx"),
        ),
    ]
