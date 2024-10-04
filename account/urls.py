from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("favorite/", views.WishListView.as_view(), name="wishlist_list"),
    path("user-orders/", views.UserOrdersView.as_view(), name="user_orders"),
    path(
        "favorite/change/<slug>/",
        views.ChangeWishListView.as_view(),
        name="change_wishlist",
    ),
    # Address
    path("addresses/", views.AddressListView.as_view(), name="addresses"),
    path(
        "address/set_defulat/<id>/",
        views.SetDefaultAddressView.as_view(),
        name="set_default_address",
    ),
    path("addresses/create/", views.AddressCreateView.as_view(), name="create_address"),
    path(
        "addresses/update/<pk>/",
        views.AddressUpdateView.as_view(),
        name="update_address",
    ),
    path(
        "addresses/delete/<pk>/",
        views.AddressDeleteView.as_view(),
        name="delete_address",
    ),
    path("register/", views.RegistrationView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # Account verification
    path(
        "account_verification/",
        views.AccountVerificationView.as_view(),
        name="verification",
    ),
    path(
        "submit_verification_code/",
        views.SubmitVerificationCodeView.as_view(),
        name="submit_verification_code",
    ),
]
