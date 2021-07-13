from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Product

# Create your views here.
class HomeView(ListView):
    model = Product
    paginate_by = 10
    template_name = 'index.html'
    ordering = ['-id']

#def homeView(request):
#    products = Product.objects.all()
