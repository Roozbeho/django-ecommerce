from django.db import models


class ProductQuerySet(models.QuerySet):

    def filter_and_order(self, active=False, order_by=None, asc=True):
        if active:
            qs = self.filter(is_active=active)
        else:
            qs = self.all()

        if order_by == "price":
            return qs.order_by_price(asc)

        elif order_by == "viewed":
            return qs.order_by_most_viewed(asc)

        elif order_by == "created_time":
            return qs.order_by_created_time(asc)

        return qs
    
    def order_by_most_viewed(self, asc):
        if asc:
            return self.order_by("viewed")
        return self.order_by("-viewed")

    def order_by_created_time(self, asc):
        if asc:
            return self.order_by("created_at")
        return self.all()
    

    def order_by_price(self, asc):
        if asc:
            return self.order_by("price")
        return self.order_by("-price")


class ProductCustomManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def filter_and_order(self, active=False, order_by=None, asc=True):
        return self.get_queryset().filter_and_order(active, order_by, asc)
