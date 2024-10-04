from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_type",
        "discount_amount",
        "max_uses",
        "max_uses_per_user",
        "min_price",
        "is_active",
    ]
