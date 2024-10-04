from .basket import Basket


def Basket_Length(request):
    return {"basket_length": Basket(request)}
