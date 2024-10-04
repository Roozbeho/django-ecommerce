from typing import Any
from django.contrib import messages
from django.db.models import F, OuterRef, Prefetch, Subquery, Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView, CreateView

from .models import Category, Product, Sub_Category, Review, ProductImage
from .forms import ReviewForm
from order.models import Order
from account.views import VerificationAccountRequiredMixin

# from django.core.cache import cache


class HomeView(ListView):
    template_name = "shop/home.html"
    context_object_name = "products"
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["most_viewed_product"] = Product.objects.filter_and_order(
            order_by="viewed", asc=False
        ).prefetch_related(Prefetch("product_images", queryset=ProductImage.objects.filter(is_cover=True)))[:6]
        return context

    def get_queryset(self):
        return (
            super(HomeView, self)
            .get_queryset()
            .prefetch_related(Prefetch("product_images", queryset=ProductImage.objects.filter(is_cover=True)))[:6]
        )


class CategoryView(View):
    template_name = "shop/category.html"

    def get(self, request, category_slug, *args, **kwargs):
        subq = Subquery(
            Product.objects.filter(sub_category_id=OuterRef("sub_category_id")).values_list("id", flat=True)[:6]
        )

        category = (
            Category.objects.filter(slug=category_slug)
            .prefetch_related("subcategories")
            .prefetch_related(
                Prefetch(
                    "subcategories__products",
                    queryset=Product.objects.filter(id__in=subq),
                )
            )
            .prefetch_related(
                Prefetch(
                    "subcategories__products__product_images", queryset=ProductImage.objects.filter(is_cover=True)
                )
            )[:6]
        )

        context = {
            "category": category,
            "category_name": Category.objects.get(slug=category_slug),
        }

        return render(request, self.template_name, context)


class SubCategoriesView(ListView):
    template_name = "shop/sub_categories.html"
    context_object_name = "products"
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subcategory_name"] = Sub_Category.objects.get(slug=self.kwargs["sub_category"])
        return context

    def get_queryset(self):
        if self.request.GET.get("sort") == "price_asc":
            qs = Product.objects.filter_and_order(order_by="price", asc=True).filter(
                sub_category__slug=self.kwargs["sub_category"]
            )
        elif self.request.GET.get("sort") == "price_desc":
            qs = Product.objects.filter_and_order(order_by="price", asc=False).filter(
                sub_category__slug=self.kwargs["sub_category"]
            )
        elif self.request.GET.get("sort") == "oldest":
            qs = Product.objects.filter_and_order(order_by="created_time", asc=True).filter(
                sub_category__slug=self.kwargs["sub_category"]
            )
        elif self.request.GET.get("sort") == "viewed":
            qs = Product.objects.filter_and_order(order_by="viewed", asc=False).filter(
                sub_category__slug=self.kwargs["sub_category"]
            )
        else:
            qs = Product.objects.filter(sub_category__slug=self.kwargs["sub_category"])

        return qs.prefetch_related(Prefetch("product_images", queryset=ProductImage.objects.filter(is_cover=True)))


# class ProductDetailView(DetailView):
#     # TODO: pepole also buys this :
#     def dispatch(self, request, *args, **kwargs):
#         obj = self.get_queryset()
#         obj.update(viewed=F("viewed") + 1)
#         return super().dispatch(request, *args, **kwargs)

#     context_object_name = "product"
#     template_name = "shop/product_detail.html"


#     def get_queryset(self):
#         return (
#             Product.objects.filter(slug=self.kwargs["slug"])
#             .prefetch_related("product_images")
#             .prefetch_related("productspecificationvalue_set")
#             .prefetch_related("reviews")
#             .prefetch_related('reviews__customer')
#         )
class ProductDetailView(ListView):
    # TODO: pepole also buys this :
    def dispatch(self, request, *args, **kwargs):
        # obj = self.get('products')
        # obj.update(viewed=F("viewed") + 1)
        # Product.objects.filter(slug=self.kwargs['slug']).update(viewed=F("viewed")+1)
        # product = Product.objects.get(slug=self.kwargs['slug'])
        # product.viewed += 1
        # product.save()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = "reviews"
    template_name = "shop/product_detail.html"
    model = Review
    paginate_by = 3

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["products"] = (
            Product.objects.filter(slug=self.kwargs["slug"])
            .prefetch_related("product_images")
            .prefetch_related("productspecificationvalue_set")
        )
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(product__slug=self.kwargs["slug"]) & Q(is_active=True))
            .select_related("customer")
        )


class CreateReviewView(VerificationAccountRequiredMixin, CreateView):
    template_name = "shop/create_review.html"
    form_class = ReviewForm

    def dispatch(self, request, *args, **kwargs):
        self.product = Product.objects.get(slug=self.kwargs["slug"])
        if not Review.is_valid(self.request.user, self.product):
            messages.warning(request, "you already have review on this product")
            return redirect(request.META["HTTP_REFERER"])

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.product = self.product

        # check user buy product or not
        if Order.objects.filter(customer=self.request.user).filter(orderitems__product=self.product).exists():
            form.instance.is_buyer = True

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.kwargs["slug"]})
