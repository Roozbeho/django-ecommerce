from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .basket import Basket


class BasketView(View):
    template_name = "basket/basket.html"

    def get(self, request, *args, **kwargs):
        basket = Basket(request)
        return render(request, self.template_name, {"basket": basket})


class AddBasketView(View):
    def post(self, request, *args, **kwargs):
        basket = Basket(request)
        print("here", "*" * 500)

        if request.POST.get("action") == "add":
            product_id = request.POST.get("product_id")
            quantity = request.POST.get("quantity")

            basket.add(str(product_id), int(quantity))
            return JsonResponse({"basket_length": basket.__len__()})


class RemoveBasketView(View):
    def post(self, request, *args, **kwargs):
        basket = Basket(request)
        print("here1", "*" * 50)

        if request.POST.get("action") == "remove":
            print("here2", "*" * 50)
            product_id = request.POST.get("productid")

            basket.remove(str(product_id))

            return JsonResponse(
                {
                    "basket_length": basket.__len__(),
                    "total_price": basket.get_total_price_before_discount(),
                }
            )


class UpdateBasketView(View):
    def post(self, request, *args, **kwargs):
        basket = Basket(request)

        if request.POST.get("action") == "update":
            product_id = request.POST.get("productid")
            quantity = request.POST.get("quantity")
            update = request.POST.get("update")

            if update == True:
                print(True, "*" * 50)

            basket.add(product_id, int(quantity), update)

            return JsonResponse(
                {
                    "basket_length": basket.__len__(),
                    "total_price": basket.get_total_price_before_discount(),
                }
            )
