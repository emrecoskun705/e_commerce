from django.urls import path
from .views import (
    ProductList, 
    TrendProductList, 
    FavouriteProductList,)

app_name = 'api'

urlpatterns = [
    path('product-list/', ProductList.as_view(), name='product-list'),
    path('trend-product-list/', TrendProductList.as_view(), name='trend-list'),
    path('favourite-product-list/', FavouriteProductList.as_view(), name='favourite-product-list'),
]