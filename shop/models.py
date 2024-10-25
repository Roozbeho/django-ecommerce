import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .manager import ProductCustomManager


class SlugNameAbstract(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"), unique=True)
    slug = models.SlugField(max_length=255, verbose_name=_("Safe Url"), unique=True)

    class Meta:
        abstract = True


class TimestampAbstract(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(SlugNameAbstract, TimestampAbstract):
    description = models.CharField(max_length=1000)
    image = models.ImageField(
        upload_to="category/",
        help_text="Upload Category Image",
        verbose_name=_("Category Image"),
        default="category/default.png",
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["slug"])]

    def get_absolute_url(self):
        return reverse("shop:category", args=[self.slug])

    def __str__(self):
        return self.name


class Sub_Category(SlugNameAbstract):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["slug"])]

    def get_absolute_url(self):
        return reverse("shop:subcategory", args=[self.slug])

    def __str__(self):
        return self.name


class Product(SlugNameAbstract, TimestampAbstract):
    sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE, related_name="products")
    wishlist = models.ManyToManyField(get_user_model(), blank=True, related_name="wishlist_products")

    description = models.TextField(blank=True, help_text=_("Information about product"))
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    viewed = models.PositiveIntegerField(default=0)

    objects = ProductCustomManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["viewed"])
        ]

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.slug])

    def get_cover_image(self):
        # It's return the products image which is_cover
        return self.product_images.filter(is_cover=True).first()

    @property
    def product_avg_rating(self):
        return self.raintgs.aggregate(avg_rating=Avg("rating")).get("avg_rating", 0)

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductSpecificationValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    productspecification = models.ForeignKey(ProductSpecification, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ("product", "productspecification")

    def __str__(self):
        return f"{self.product.name} - {self.productspecification.name}: {self.value}"


def Image_Path(instance, filename):
    return f"product/{instance.product.sub_category.category.slug}/{instance.product.sub_category.slug}/{instance.product.slug}/{filename}"


class ProductImage(TimestampAbstract):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(
        upload_to=Image_Path,
        help_text="Upload Product Image",
        verbose_name=_("Product Image"),
        default="image/product/default.png",
    )
    alt = models.CharField(max_length=225, blank=True)
    is_cover = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Products can have just one cover,
        check other images and change is_cover to False
        """
        if self.is_cover:
            ProductImage.objects.filter(Q(is_cover=True) & Q(product=self.product)).exclude(id=self.id).update(
                is_cover=False
            )
        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {'Cover' if self.is_cover else 'Image'}"


class Review(TimestampAbstract):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name="reviews", null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=50, verbose_name=_("title"))
    description = models.TextField()
    is_buyer= models.BooleanField(default=False, help_text=_("Is thise user buy this product"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["customer", "product"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_active"]),
        ]

    @classmethod
    def is_valid(cls, customer, product):
        """
        Check if the customer has already made a review or rating for the product.

        its prevent customer from reviewing a product more than once
        """
        if Review.objects.filter(Q(customer=customer)&Q(product=product)&Q(is_active=True)).exists():
            return False
        return True

    def __str__(self):
        return f"{self.customer.email} make a Review on {self.product.name} product"


# class Rating(models.Model):
#     customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name="ratings", null=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
#     rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])

#     class Meta:
#         indexes = [models.Index(fields=["rating"]), models.Index(fields=["product"])]

#     @classmethod
#     def is_valid(self, customer, product):
#         """
#         Check if the customer has already rated the product.

#         its prevent customer from rating a product more than once
#         """
#         if Rating.objects.filter(Q(customer=customer)&Q(product=product)).exists():
#             return False
#         return True

#     def __str__(self):
#         return f"{self.customer.email} rate {self.rating} to {self.product.name} product"
