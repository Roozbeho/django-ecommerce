from django.contrib import admin
from django.urls import reverse
from django.utils.html import urlencode
from django.utils.safestring import mark_safe

from .models import Address, Customer, OtpCode


# class AddressAdmin(admin.StackedInline):
    # model = Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['get_fullname', 'customer__email', 'phone_number', 'state', 'city', 'is_default']
    list_filter = ['state', 'city']
    search_fields = ['customer', 'first_name__istartswith', 'last_name__istartswith']
    list_select_related = ['customer']
    list_per_page = 25

    def get_fullname(self, address):
        return address.first_name + ' ' + address.last_name
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_verified", 'address', 'order']
    list_filter = ['is_superuser', 'is_verified', 'is_active']
    search_fields = ['username__istartswith', 'email__istartswith']
    list_per_page = 25



    @admin.display(description='Addresses')
    def address(self, customer):
        url = (
            reverse('admin:account_address_changelist')
            + '?' + urlencode({'customer__id':str(customer.id)})
        )
        return mark_safe(f"<a href='{url}'>User Addresses</a>")
    
    @admin.display(description='Orders')
    def order(self, customer):
        url = (
            reverse('admin:order_order_changelist')
            + '?' + urlencode({'customer__id':str(customer.id)})
        )
        return mark_safe(f"<a href='{url}'>User Orders</a>")
    
@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    readonly_fields = ["otp_code"]
    list_display = ["email", "otp_code", "is_active", "created_at"]
    search_fields = ["email", "created_at"]
    list_filter = ["email", "created_at"]
