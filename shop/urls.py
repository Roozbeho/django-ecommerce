from django.urls import path

from . import views

app_name = "shop"


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "category/<category_slug>/",
        views.CategoryView.as_view(),
        name="category",
    ),
    path(
        "sub_category/products/<sub_category>/",
        views.SubCategoriesView.as_view(),
        name="subcategory",
    ),
    # path('categroy/<category>/', views.SubCategoriesView.as_view(), name="subcategory"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path('create-review/<slug>/', views.CreateReviewView.as_view(), name='create_review'),
]
