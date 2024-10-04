from django.contrib import admin

from .models import DeliveryOptions, Order, OrderItem, PaymentDetails


class PaymentDetailsTabularInline(admin.StackedInline):
    model = PaymentDetails
    can_delete = False
    extra = 0


class OrderItemTabularInline(admin.TabularInline):
    model = OrderItem
    can_delete = False
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "fullname",
        "order_price",
        "pay_status",
        "order_status",
        "created_at",
    ]
    inlines = [PaymentDetailsTabularInline, OrderItemTabularInline]


@admin.register(DeliveryOptions)
class DeliveryOptionsAdmin(admin.ModelAdmin):
    list_display = ["delivery_type", "price", "is_active"]
