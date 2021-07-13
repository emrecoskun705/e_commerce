from django.shortcuts import render
from django.views.generic import ListView

# Create your views here.
def homeView(request):
    return  render(request, 'index.html')