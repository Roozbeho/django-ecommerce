# Generated by Django 5.1.1 on 2024-09-26 08:16

import account.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_otpcode_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="otpcode",
            name="is_valid",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="otpcode",
            name="otp_code",
            field=models.CharField(
                blank=True,
                default=account.utils.create_random_code,
                editable=False,
                max_length=8,
            ),
        ),
    ]
