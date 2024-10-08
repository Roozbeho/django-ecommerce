import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site


from order.tasks import send_email
from .manager import CustomCustomerManager
from .utils import create_random_code
from .token import Change_Password_token


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, verbose_name="E-mail", unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomCustomerManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        indexes = [models.Index(fields=["email"]), models.Index(fields=["username"])]

    def __str__(self):
        return self.username


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    first_name = models.CharField(max_length=50, verbose_name="First name")
    last_name = models.CharField(max_length=50, verbose_name="Last name")
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
    address_line_2 = models.CharField(max_length=255, verbose_name="Address second line")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["id"])]

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(is_default=True).exclude(id=self.id).update(is_default=False)
        return super(Address, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name


class OtpCode(models.Model):
    email = models.EmailField(max_length=255, verbose_name="E-mail")
    otp_code = models.CharField(max_length=8, blank=True, editable=False, default=create_random_code)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def send_verification_email(self, subject, message):
        print(message)
        send_mail(
            subject=subject,
            message=message,
            recipient_list=[self.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
        )
        return True

    def validate_verification_code(self, code):
        if str(self.otp_code) == str(code):
            if timezone.now() <= self.created_at + timedelta(minutes=5):
                Customer.objects.filter(email=self.email).update(is_verified=True)
                return True
        return False

    def save(self, *args, **kwargs):
        q = OtpCode.objects.filter(email=self.email).exclude(id=self.id)
        if q.exists:
            q.update(is_active=False)
        return super(OtpCode, self).save(*args, **kwargs)

    def __str__(self):
        return self.email
