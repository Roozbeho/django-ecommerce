from django.db import models


class ProductQuerySet(models.QuerySet):
    def order_by_most_viewed(self, asc):
        if asc:
            return self.order_by("viewed")
        return self.order_by("-viewed")

    def order_by_oldest(self):
        return self.order_by("created_at")

    def order_by_price(self, asc):
        if asc:
            return self.order_by("price")
        return self.order_by("-price")


class ProductCustomManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def filter_and_order(self, active=False, order_by=None, asc=True):
        if active:
            qs = self.get_queryset().filter(is_active=active)
        else:
            qs = self.get_queryset().all()

        if order_by == "price":
            return qs.order_by_price(asc)

        elif order_by == "viewed":
            return qs.order_by_most_viewed(asc)

        elif order_by == "created_time":
            return qs.order_by_oldest()

        return qs
