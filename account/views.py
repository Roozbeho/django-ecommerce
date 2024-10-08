from django.db.models.query import QuerySet
from basket.basket import Basket
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, FormView
from order.models import Order
from shop.models import Product
from django.contrib.auth.views import PasswordChangeView

from .forms import (AccountVerificationForm, AddressForm, LoginForm,
                    RegistrationForm, ChangeCustomerInformationForm, CustomPasswordChangeForm)
from .models import Address, OtpCode, Customer

class VerificationAccountRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(request.user, 'is_verified') and not request.user.is_verified:
            return render(request, "account/not_verified_account.html")
        return response
        # return super().dispatch(request, *args, **kwargs)


class DashboardView(VerificationAccountRequiredMixin, View):
    template_name = "account/dashboard/dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class RegistrationView(View):
    form_class = RegistrationForm
    template_name = "account/register.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("account:login")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    form_class = LoginForm
    template_name = "account/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "You already singed in, please loggout first")
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if user:
                login(request, user)

                if not user.is_verified:
                    return redirect("account:verification")
                else:
                    return redirect("/")

        return render(request, self.template_name, {"form": form})


class LogoutView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, "account/logout.html")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("account:login")


class AccountVerificationView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(request.user, 'is_verified') and request.user.is_verified:
            return redirect("/")
        return response

    def get(self, request, *args, **kwargs):
        user_email = request.user.email
        otp_code = OtpCode.objects.create(email=user_email)

        # verification email setup
        subject = "Account verification code"
        message = render_to_string(
            "account/account_verification_form.html",
            {"code": otp_code.otp_code, "customer": request.user.username},
        )
        otp_code.send_verification_email(subject=subject, message=message)

        return redirect("account:submit_verification_code")


class SubmitVerificationCodeView(LoginRequiredMixin, View):
    form_class = AccountVerificationForm

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(request.user, 'is_verified') and request.user.is_verified:
            return redirect("/")
        return response

    def get(self, request, *args, **kwargs):
        return render(request, "account/verification_code_form.html", {"form": self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                result = OtpCode.objects.get(
                    Q(is_active=True) & Q(email=request.user.email)
                ).validate_verification_code(code)
                if result:
                    return HttpResponse("Your account has been verified successfully")
                return HttpResponse("something went wrong, please try again")

            except:
                return HttpResponse("something went wrong, please try again2")

        return render(request, "account/verification_code_form.html", {"form": form})


class WishListView(VerificationAccountRequiredMixin, ListView):
    template_name = "account/dashboard/wishlist.html"
    context_object_name = "favorite"

    def get_queryset(self):
        return self.request.user.wishlist_products.all().prefetch_related('product_images')


class ChangeWishListView(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)
        if product.wishlist.filter(id=request.user.id).exists():

            product.wishlist.remove(request.user.id)
            messages.warning(request, "product has been removed from favorites")
        else:

            product.wishlist.add(request.user)
            messages.success(request, "product has been added to favorites")

        return HttpResponseRedirect(request.META["HTTP_REFERER"])


class AddressListView(VerificationAccountRequiredMixin, ListView):
    template_name = "account/address/addresses.html"
    context_object_name = "addresses"
    model = Address

    def get_queryset(self):
        return super(AddressListView, self).get_queryset().filter(customer=self.request.user)


class SetDefaultAddressView(VerificationAccountRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        print("selcome", "*" * 50)
        basket = Basket(request)

        address = get_object_or_404(Address, id=id)
        address.is_default = True
        address.save()

        basket.set_delivery_address(str(address.id))

        return HttpResponseRedirect(request.META["HTTP_REFERER"])


class AddressCreateView(VerificationAccountRequiredMixin, CreateView):
    template_name = "account/address/create_address.html"
    model = Address
    form_class = AddressForm
    success_url = reverse_lazy("account:addresses")

    def form_valid(self, form):
        print("here")
        form.instance.customer = self.request.user
        return super().form_valid(form)


class AddressUpdateView(VerificationAccountRequiredMixin, UpdateView):
    template_name = "account/address/update_address.html"
    model = Address
    form_class = AddressForm
    success_url = reverse_lazy("account:addresses")


class AddressDeleteView(VerificationAccountRequiredMixin, DeleteView):
    template_name = "account/address/address_confirm_delete.html"
    model = Address
    success_url = reverse_lazy("account:addresses")


class UserOrdersView(VerificationAccountRequiredMixin, ListView):
    template_name = "account/dashboard/user_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            Order.objects.filter(customer=self.request.user)
            .annotate(qty=Count("orderitems__id"))
            .prefetch_related("payments")
        )


class ChangeCustomerInformationView(VerificationAccountRequiredMixin ,FormView):
    template_name = 'account/dashboard/change_customer_information.html'
    form_class = ChangeCustomerInformationForm
    success_url = reverse_lazy('account:dashboard')
    
    def get_initial(self):
        return {
            'email': self.request.user.email,
            'username': self.request.user.username
        }
      
    def post(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial_dict, data=request.POST)
        if form.is_valid():
            if request.user.email != form.cleaned_data['email']:
                raise ValueError('You cannot change your email address')

            request.user.username = form.cleaned_data['username']
            request.user.save()

            messages.success(request, 'your username changed successfully')
            return redirect('account:dashboard')
        return render(request, self.template_name, {'form': form})
    

class DeleteAccountView(VerificationAccountRequiredMixin, View):
    template_name = 'account/dashboard/delete_account.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        customer = Customer.objects.get(email=request.user.email)
        customer.is_active = False
        customer.save()
        messages.warning(request, 'Your account was deleted successfully')
        return redirect('account:register')
    

class ChangePasswordView(VerificationAccountRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('account:login')
    template_name = 'account/account_management/change_password.html'

    def form_valid(self, form):
        logout(self.request)
        messages.success(self.request, 'your password changed, please log in again')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for error in form.errors:
            messages.warning(self.request, error)
        return super().form_invalid(form)
    