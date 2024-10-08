import json
from decimal import Decimal
from typing import Any
import weasyprint

from django.http.response import HttpResponse
from account.models import Address
from account.views import VerificationAccountRequiredMixin
from basket.basket import Basket
from coupon.forms import CouponForm
from coupon.models import Coupon
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import ListView, TemplateView
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from django.utils.html import strip_tags
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.staticfiles.storage import staticfiles_storage


from .models import DeliveryOptions, Order, OrderItem, PaymentDetails
from .paypal import PayPalClient
from .tasks import send_order_email


class BasketNotEmptyRequired:
    def dispatch(self, request, *args, **kwargs):
        if request.session["basket"].__len__() == 0:
            messages.warning(request, "your basket is empty")
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)


class DeliveryAddressChoice(VerificationAccountRequiredMixin, BasketNotEmptyRequired, ListView):
    template_name = "order/delivery_address.html"
    context_object_name = "addresses"
    model = Address

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["basket"] = Basket(self.request)
        return context

    def get_queryset(self):
        return super(DeliveryAddressChoice, self).get_queryset().filter(customer=self.request.user)


class DelieryOptionchoices(VerificationAccountRequiredMixin, BasketNotEmptyRequired, View):
    template_name = "order/delivery_options.html"

    def dispatch(self, request, *args, **kwargs):
        self.basket = Basket(request)
        if not self.basket.session.get("delivery_address"):
            messages.warning(request, "please set an delivery address first")
            return redirect("order:order_address")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return DeliveryOptions.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"delivery_options": self.get_queryset})

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "update":
            deliveryid = request.POST.get("deliveryid")
            self.basket.add_delivery_option(deliveryid)

            return JsonResponse({"delivery_type": self.basket.session["delivery_option"]["delivery_type"]})


class PaymentView(VerificationAccountRequiredMixin, BasketNotEmptyRequired, View):
    template_name = "order/payment/payment.html"
    form_class = CouponForm

    def dispatch(self, request, *args, **kwargs):
        self.basket = Basket(request)

        if not self.basket.session.get("delivery_address"):
            messages.warning(request, "please set an delivery address first")
            return redirect("order:order_address")

        if not self.basket.session.get("delivery_option"):
            messages.warning(request, "please set an delivery option first")
            return redirect("order:delivery_option")

        delivery_address = Address.objects.get(id=self.basket.session["delivery_address"]["id"])
        delivery_option = DeliveryOptions.objects.get(id=self.basket.session["delivery_option"]["id"])

        self.context = {
            "form": self.form_class(price=Decimal(self.basket.get_final_price())),
            "basket": self.basket,
            "delivery_address": delivery_address,
            "delivery_option": delivery_option,
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
        }

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(price=Decimal(self.basket.get_final_price()), data=request.POST)
        if form.is_valid():
            self.basket.add_coupon(form.cleaned_data["code"])

            self.context["form"] = form
            self.context["is_coupon_valid"] = True

            return render(request, self.template_name, self.context)

        self.context["form"] = form
        return render(request, self.template_name, self.context)


class PaymentCompleteView(VerificationAccountRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        paypal_client = PayPalClient()
        basket = Basket(request)

        data_body = json.loads(request.body)
        order_id = data_body["orderID"]

        response = paypal_client.client.execute(OrdersCaptureRequest(order_id))

        address = Address.objects.get(id=basket.session["delivery_address"]["id"])

        coupon = None
        if basket.session.get("coupon"):
            coupon = Coupon.objects.get(id=basket.session["coupon"]["coupon_id"])

        if basket.session.get("delivery_option"):
            delivery_option = DeliveryOptions.objects.get(id=basket.session["delivery_option"]["id"])

        order = Order.objects.create(
            customer=request.user,
            delivery=delivery_option,
            fullname=address.first_name + address.last_name,
            phone_number=address.phone_number,
            postal_code=address.postal_code,
            state=address.state,
            city=address.city,
            address_line_1=address.address_line_1,
            address_line_2=address.address_line_2,
            order_price=Decimal(basket.get_total_price_before_discount()),
            pay_status=True,
            order_status=Order.SHIPPING,
        )

        order.apply_delivery(delivery_option)
        if coupon:
            order.discount_amount = order.apply_coupon(coupon)

        for item in basket:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"],
            )

        PaymentDetails.objects.create(
            order=order,
            platform_provider="Paypal",
            total_price=basket.get_final_price(),
            payment_id=response.result.id,
        )

        # Send Order info To User

        subject = "Your order made on successfully"
        messages = render_to_string("order/order_made_email.html", {"order": order})
        send_order_email.delay(subject, messages, request.user.email)

        return JsonResponse("Payment completed!", safe=False)


class PaymentSuccessfulView(VerificationAccountRequiredMixin, View):
    template_name = "order/payment/payment_successful.html"

    def get(self, request, *args, **kwargs):
        try:
            basket = Basket(request)
            basket.clear()
            return render(request, self.template_name)
        except:
            return redirect("account:dashboard")

class OrderReceiptAdminView(TemplateView):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_staff:
            messages.warning(request, 'only admins can view')
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)
    
    template_name = 'admin/order/order/order_receipt.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(id=self.kwargs['order_id']).select_related('customer').prefetch_related('orderitems').prefetch_related('payments')
        return context
    
class OrderReceiptView(TemplateView):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        self.order = Order.objects.filter(id=self.kwargs['order_id']).select_related('customer')
        if self.order.first().customer != request.user:
            return Http404
        return super().dispatch(request, *args, **kwargs)

    template_name = 'order/order_receipt.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['orders'] = self.order.prefetch_related('orderitems').prefetch_related('payments')
        return context

class render_order_receipt_to_PDF(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Http404
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, order_id):

        orders = get_object_or_404(
            Order.objects.prefetch_related('orderitems').select_related('payments'),
            id=order_id)
        
        html = render_to_string('order/order_receipt_pdf.html', {'order': orders}, request=request)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=order_{orders.id}.pdf'
        
        css_path = staticfiles_storage.path('css/order_receipt_pdf.css')
        
        weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            response,
            stylesheets=[weasyprint.CSS(css_path)])
        
        return response

