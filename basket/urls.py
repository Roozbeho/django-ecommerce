from django.urls import path

from . import views

app_name = "basket"

urlpatterns = [
    path("", views.BasketView.as_view(), name="view"),
    path("add/", views.AddBasketView.as_view(), name="add"),
    path("remove/", views.RemoveBasketView.as_view(), name="remove"),
    path("update/", views.UpdateBasketView.as_view(), name="update"),
]
