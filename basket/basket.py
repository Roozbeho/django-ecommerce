from decimal import Decimal

from account.models import Address
from coupon.models import Coupon
from order.models import DeliveryOptions
from shop.models import Product


class Basket:
    def __init__(self, request):
        self.session = request.session

        if not self.session.get("basket"):
            self.session["basket"] = {}

        self.basket = self.session["basket"]

    def __iter__(self):
        basket = self.basket.copy()
        product_ids = list(map(int, basket.keys()))

        for product in Product.objects.filter(id__in=product_ids):
            self.basket[str(product.id)]["product"] = product

        for item in self.basket.values():
            item["total_price"] = Decimal(item["price"]) * int(item["quantity"])
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.basket.values())

    def add(self, id, qty, update=False):
        product = Product.objects.get(id=int(id))

        if id not in self.basket:
            self.basket[id] = {"price": str(product.price), "quantity": qty}

        if update:
            self.basket[id]["quantity"] = qty

        self.clear_discount_if_basket_changed()
        self.clear_delivery_address_and_option_if_basket_change()

        self.save()

    def remove(self, id):
        print("here", "*" * 50)
        if id in self.basket:
            del self.basket[id]

        self.clear_discount_if_basket_changed()
        self.clear_delivery_address_and_option_if_basket_change()

        self.save()

    def set_delivery_address(self, id):
        self.session["delivery_address"] = {"id": id}

        self.clear_discount_if_basket_changed()

        self.save()

    def add_delivery_option(self, id):
        delivery = DeliveryOptions.objects.get(id=id)

        self.session["delivery_option"] = {
            "id": id,
            "delivery_type": delivery.delivery_type,
            "price": str(delivery.price),
        }

        self.clear_discount_if_basket_changed()

        self.save()

    def add_coupon(self, code):
        coupon = Coupon.objects.get(code=code)

        self.session["coupon"] = {
            "coupon_id": str(coupon.id),
            "discount_type": str(coupon.discount_type),
            "discount_amount": str(coupon.discount_amount),
        }

        self.save()

    def get_total_price_before_discount(self):
        return sum(Decimal(item["price"]) * int(item["quantity"]) for item in self.basket.values())

    def get_total_price_after_appling_delivery_price(self):
        return self.get_total_price_before_discount() + Decimal(self.session["delivery_option"]["price"])

    # def get_total_price_after_discount(self):
    #     if self.session.get("coupon"):
    #         price_before_discount = self.get_total_price_before_discount()

    #         coupon = Coupon.objects.get(id=self.session["coupon"]["coupon_id"])

    #         return price_before_discount - coupon.calculate_discount(
    #             price_before_discount
    #         )
    #     return self.get_total_price_before_discount()

    def get_final_price(self):
        # """
        # return delivery price + total price of basket + apply coupon
        # """
        # return f'{(self.get_total_price_after_discount() \
        #     + Decimal(self.session["delivery_option"]['price'])):.2f}'
        if self.session.get("coupon"):
            price_before_discount = self.get_total_price_after_appling_delivery_price()

            coupon = Coupon.objects.get(id=self.session["coupon"]["coupon_id"])

            final_price = price_before_discount - coupon.calculate_discount(Decimal(price_before_discount))
        else:
            final_price = self.get_total_price_after_appling_delivery_price()
        return f"{final_price:.2f}"

    def clear_discount_if_basket_changed(self) -> None:
        """
        Clears the discount from the basket if the basket has been changed.

        This function checks if a coupon is currently applied to the basket. If a coupon is found,
        it removes the coupon from the session and saves the changes. This ensures that the discount
        is cleared when the basket is modified.

        """
        if self.session.get("coupon"):
            del self.session["coupon"]
            self.save()

        return

    def clear_delivery_address_and_option_if_basket_change(self) -> None:
        """
        Clears the delivery address and delivery option from the session if the basket has been changed.

        This function checks if the delivery address and delivery option are currently set in the session.
        If either of them is found, it removes them from the session. This ensures that the delivery
        address and delivery option are cleared when the basket is modified.
        """
        if self.session.get("delivery_address"):
            del self.session["delivery_address"]

        if self.session.get("delivery_option"):
            del self.session["delivery_option"]

        self.save()
        return

    def clear(self):
        del self.session["delivery_option"]
        del self.session["delivery_address"]
        if self.session.get("coupon"):
            del self.session["coupon"]
        del self.session["basket"]

        self.save()

    def save(self):
        self.session.modified = True
