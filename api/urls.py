from django.urls import path
from .views import ProductList, TrendProductList

app_name = 'api'

urlpatterns = [
    path('product-list/', ProductList.as_view(), name='product-list'),
    path('trend-product-list/', TrendProductList.as_view(), name='trend-list'),
]