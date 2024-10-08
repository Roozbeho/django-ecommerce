from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('admin/order/order/order-receipt/<id>/', TemplateView.as_view(template_name='admin/order/order/order_receipt.html'), name='order_receipt'),
    path("account/", include("account.urls", namespace="account")),
    path("basket/", include("basket.urls", namespace="basket")),
    path("coupon/", include("coupon.urls", namespace="coupon")),
    path("order/", include("order.urls", namespace="order")),
    path("", include("shop.urls", namespace="shop")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
