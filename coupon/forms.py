from typing import Any

from django import forms

from .models import Coupon


class CouponForm(forms.Form):
    code = forms.CharField(max_length=10)

    def __init__(self, price, *args, **kwargs):
        self.order_price = price
        print(self.order_price, "roozbeh" * 10)
        super(CouponForm, self).__init__(*args, **kwargs)

        self.fields["code"].widget.attrs.update({"class": "form-control", "placeholder": "Discount Code"})

    def clean_code(self):
        code = self.cleaned_data["code"]

        try:
            coupon = Coupon.objects.get(code=code)
            print(coupon.is_valid(self.order_price))
            if not coupon.is_valid(self.order_price):
                raise forms.ValidationError("You cant use thise coupon")
        except Exception as e:
            print(e)
            raise forms.ValidationError("Coupon is not valid")

        return code
