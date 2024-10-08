from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    path("order-address/", views.DeliveryAddressChoice.as_view(), name="order_address"),
    path("delivery-option/", views.DelieryOptionchoices.as_view(), name="delivery_option"),
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path(
        "payment/complete/",
        views.PaymentCompleteView.as_view(),
        name="payment_complete",
    ),
    path(
        "payment/sccessful/",
        views.PaymentSuccessfulView.as_view(),
        name="payment_successful",
    ),
    path('admin/order-receipt/<order_id>/', views.OrderReceiptAdminView.as_view(), name='order_receipt_admin'),
    path('order-receipt/<order_id>/', views.OrderReceiptView.as_view(), name='order_receipt'),
    path('render-to-pdf/<order_id>/', views.render_order_receipt_to_PDF.as_view(), name='render_receipt_to_pdf'),
]
