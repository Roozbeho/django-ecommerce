from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    ProductSpecificationValue,
    Review,
    Sub_Category,
)
from django.urls import reverse
from django.utils.html import urlencode
from django.utils.safestring import mark_safe
from django.db.models import Count


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "sub_category"]
    list_filter = ["name", "is_active", "created_at"]
    search_fields = ["name__istartswith"]
    prepopulated_fields = {"slug": ["name"]}
    list_per_page = 25
    admin_priority = 1

    @admin.display(description="sub categories")
    def sub_category(self, category):
        url = (
            reverse("admin:shop_sub_category_changelist")
            + "?"
            + urlencode({"category__id": str(category.id)})
        )
        return mark_safe(
            f'<a href="{url}">{category.subcategory_count} related sub categories</a>'
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(subcategory_count=Count("subcategories"))
        )


@admin.register(Sub_Category)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "category__name", "product", "specification"]
    search_fields = ["name__istartswith", "category__name"]
    list_filter = ["is_active", "category__name"]
    list_select_related = ["category"]
    list_per_page = 25
    admin_priority = 2

    @admin.display(description="Products")
    def product(self, sub_category):
        url = (
            reverse("admin:shop_product_changelist")
            + "?"
            + urlencode({"sub_category__id": str(sub_category.id)})
        )

        return mark_safe(
            f'<a href="{url}">{sub_category.product_count} related products</a>'
        )

    @admin.display(description="Specifications")
    def specification(self, sub_category):
        url = (
            reverse("admin:shop_productspecification_changelist")
            + "?"
            + urlencode({"sub_category__id": str(sub_category.id)})
        )
        return mark_safe(f'<a href="{url}">related specifications</a>')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(product_count=Count("products"))


@admin.register(ProductSpecification)
class productspecificationAdmin(admin.ModelAdmin):
    list_display = ["name", "sub_category__name"]
    list_filter = ["name", "sub_category__name"]
    search_fields = ["name"]
    list_select_related = ["sub_category"]
    list_per_page = 25
    admin_priority = 3


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


class ProductImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sub_category",
        "price",
        "is_active",
        "viewed",
        "created_at",
        "review",
    ]
    list_filter = ["sub_category", "name", "price", "created_at"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name__istartswith"]
    inlines = [ProductSpecificationValueInline, ProductImageInline]
    list_per_page = 25
    admin_priority = 4

    @admin.display(description="Products")
    def review(self, product):
        url = (
            reverse("admin:shop_review_changelist")
            + "?"
            + urlencode({"product__id": str(product.id)})
        )
        return mark_safe(
            f'<a href="{url}">{product.reviews_count} reviews on thise product</a>'
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(reviews_count=Count("reviews"))


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "product",
        "title",
        "is_buyer",
        "is_active",
        "created_at",
    ]
    list_filter = ["product", "is_active", "created_at"]
    search_fields = ["customer"]
    list_per_page = 25
    admin_priority = 5


# @admin.register(Rating)
# class RatingAdmin(admin.ModelAdmin):
#     list_display = ["customer", "product", "rating"]
#     list_filter = ["customer", "product", "rating"]
