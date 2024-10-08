from ecommerce.celery import app
from django.db.models import F

from .models import Product

@app.task
def increase_product_view(product_slug):
    Product.objects.filter(slug=product_slug).update(viewed=F('viewed')+1)
    print('view added')