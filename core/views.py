from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Product, Category


class HomeView(ListView):
    model = Product
    paginate_by = 10
    template_name = 'index.html'
    ordering = ['-id']


    #This part filters categories by at the top of every trees which are roots
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(level__lt=1)
        return context

