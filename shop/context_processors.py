from .models import Category


def Categories(request):
    return {"categories": Category.objects.filter(is_active=True)}
