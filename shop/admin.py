from django.contrib import admin

from .models import (Category, Product, ProductImage, ProductSpecification,
                     ProductSpecificationValue, Review, Sub_Category)


class SubCategoryinline(admin.TabularInline):
    model = Sub_Category
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    list_filter = ["name", "is_active", "created_at"]
    prepopulated_fields = {"slug": ["name"]}

    inlines = [SubCategoryinline]


admin.site.register(ProductSpecification)


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
    ]
    list_filter = ["sub_category", "name", "price", "created_at"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProductSpecificationValueInline, ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["customer", "product", "title", "is_buyer", "is_active", "created_at"]
    list_filter = ["product", "is_active", "created_at"]
    search_fields = ["customer", "product"]


# @admin.register(Rating)
# class RatingAdmin(admin.ModelAdmin):
#     list_display = ["customer", "product", "rating"]
#     list_filter = ["customer", "product", "rating"]
