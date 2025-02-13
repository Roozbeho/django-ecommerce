from typing import Any
from django.contrib import messages
from django.db.models import OuterRef, Prefetch, Subquery, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Category, Product, Sub_Category, Review, ProductImage
from .forms import ReviewForm
from .tasks import increase_product_view
from order.models import Order
from account.views import VerificationAccountRequiredMixin


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
            .prefetch_related(
                Prefetch(
                    "product_images",
                    queryset=ProductImage.objects.filter(is_cover=True),
                )
            )[:6]
        )


class SearchProductView(View):
    template_name = "shop/search_products_result.html"

    def get(self, request, *args, **kwargs):

        search_query = request.GET.get("q")

        if not search_query:
            return redirect("/")

        products = Product.objects.filter(
            Q(name__icontains=search_query)
            | Q(slug__icontains=search_query)
            | Q(sub_category__name__icontains=search_query)
            | Q(sub_category__category__name__icontains=search_query)
        ).prefetch_related(Prefetch("product_images", queryset=ProductImage.objects.filter(is_cover=True)))
        page = request.GET.get("page", 1)

        paginator = Paginator(products, 8)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {"products": products})


class CategoryView(View):
    template_name = "shop/category.html"

    def get(self, request, category_slug, *args, **kwargs):
        subq = Subquery(
            Product.objects.filter(sub_category_id=OuterRef("sub_category_id")).values_list("id", flat=True)[:6]
        )

        category = get_object_or_404(
            Category.objects.prefetch_related("subcategories")
            .prefetch_related(
                Prefetch(
                    "subcategories__products",
                    queryset=Product.objects.filter(id__in=subq),
                )
            )
            .prefetch_related(
                Prefetch(
                    "subcategories__products__product_images",
                    queryset=ProductImage.objects.filter(is_cover=True),
                )
            ),
            slug=category_slug,
        )

        context = {"category": category}

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
        queryset = Product.objects.filter(sub_category__slug=self.kwargs["sub_category"])

        ordering_filter_mapping = {
            "price_asc": ("price", True),
            "price_desc": ("price", False),
            "oldest": ("created_time", False),
            "newest": ("created_time", True),
            "viewed": ("viewed", False),
        }

        ordering_filter = self.request.GET.get("sort")
        if ordering_filter:
            queryset = queryset.filter_and_order(
                order_by=ordering_filter_mapping[ordering_filter][0],
                asc=ordering_filter_mapping[ordering_filter][1],
            )

        try:
            if self.request.GET.get("max_price"):
                queryset = queryset.filter(price__lte=self.request.GET.get("max_price"))

            if self.request.GET.get("min_price"):
                queryset = queryset.filter(price__gte=self.request.GET.get("min_price"))

            if self.request.GET.get("in_stock"):
                queryset = queryset.filter(is_active=True)
        except:
            messages.warning(self.request, "Invalid filtering")

        return queryset.prefetch_related(
            Prefetch("product_images", queryset=ProductImage.objects.filter(is_cover=True))
        )


class ProductDetailView(ListView):
    # TODO: pepole also buys this :
    def dispatch(self, request, *args, **kwargs):
        increase_product_view.delay(self.kwargs["slug"])

        return super().dispatch(request, *args, **kwargs)

    context_object_name = "reviews"
    template_name = "shop/product_detail.html"
    model = Review
    paginate_by = 3

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["product"] = get_object_or_404(
            Product.objects.prefetch_related("product_images").prefetch_related("productspecificationvalue_set"),
            slug=self.kwargs["slug"],
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
        response = super().dispatch(request, *args, **kwargs)
        self.product = Product.objects.get(slug=self.kwargs["slug"])
        if not Review.is_valid(self.request.user, self.product):
            messages.warning(request, "you already have review on this product")
            return redirect(request.META["HTTP_REFERER"])

        return response

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.product = self.product

        # check user buy product or not
        if Order.objects.filter(customer=self.request.user).filter(orderitems__product=self.product).exists():
            form.instance.is_buyer = True

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.kwargs["slug"]})
