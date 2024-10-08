import sys
from datetime import timedelta

from account.models import OtpCode
from celery import shared_task
from celery.schedules import crontab
from django.db.models import Q
from django.utils import timezone

from ecommerce.celery import app


@app.task
def remove_unactive_otp_code():
    """
    The function calculates the expiration time by subtracting 5 minutes from the current time.
    It then retrieves all OTP codes that are either inactive or have been created before the expiration time.
    """
    expired_time = timezone.now() - timedelta(minutes=5)

    otpcodes = OtpCode.objects.filter(Q(is_active=False) | Q(created_at__lt=expired_time))

    for code in otpcodes:
        sys.stdout.write(f"removing {code.otp_code} email {code.email}")
        code.delete()

