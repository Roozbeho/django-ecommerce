from .models import Category

from .forms import ProductFilterForm

def Categories(request):
    return {"categories": Category.objects.filter(is_active=True)}

def SearchForm(request):
    return {'search_form': ProductFilterForm()}