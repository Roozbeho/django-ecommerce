import csv

from django.contrib import admin
from django.utils import timezone
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.urls import reverse, reverse_lazy

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
        "order_price",
        "pay_status",
        "order_status",
        "created_time",
        'get_receipt',
        'receipt_pdf'
    ]
    list_filter = ["created_at", "order_status", "pay_status"]
    inlines = [PaymentDetailsTabularInline, OrderItemTabularInline]
    actions = ["export_csv_file"]

    @admin.action(description="Export To csv file")
    def export_csv_file(self, request, queryset):
        """
        Export selected orderd as CSV file
        """

        filename = f"{timezone.now().date()}_sales.csv"
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

        write = csv.writer(response)
        write.writerow(
            [
                "fullname",
                "phone number",
                "postal code",
                "state",
                "city",
                "address first part",
                "address second part",
                "delivery type",
                "delivery price",
                "total price",
            ]
        )
        for obj in queryset.values_list(
            "fullname",
            "phone_number",
            "postal_code",
            "state",
            "city",
            "address_line_1",
            "address_line_2",
            "delivery__delivery_type",
            "delivery_price",
            "payments__total_price",
        ):
            write.writerow(list(obj))
        return response

    def created_time(self, obj):
        return f'{obj.created_at.strftime('%Y/%m/%d - %H:%M')}'    

    def get_receipt(self, obj):
        url = reverse_lazy('order:order_receipt_admin', args=[obj.id])
        link = '<a href="%s">%s</a>' % (url, 'order receipt')
        return mark_safe(link)
        # return mark_safe(f'<a href="{% url "" %}">Order Receipt</a>' %reverse('order_receipt'))
    
    def receipt_pdf(self, obj):
        url = reverse('order:render_receipt_to_pdf', args=[obj.id])
        link = '<a href="%s">%s</a>' % (url, 'PDF')
        return mark_safe(link)
    


@admin.register(DeliveryOptions)
class DeliveryOptionsAdmin(admin.ModelAdmin):
    list_display = ["delivery_type", "price", "is_active"]
