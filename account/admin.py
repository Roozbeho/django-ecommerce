from django.contrib import admin

from .models import Address, Customer, OtpCode


class AddressAdmin(admin.StackedInline):
    model = Address


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_verified"]
    inlines = [AddressAdmin]


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    readonly_fields = ["otp_code"]
    list_display = ["email", "otp_code", "is_active", "created_at"]
    search_fields = ["email", "created_at"]
    list_filter = ["email", "created_at"]
