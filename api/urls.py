from django.urls import path
from django.conf.urls import url
from .views import (
    ProductList, 
    TrendProductList, 
    UserFavouriteProductList,
    ProductDetail,
    UserFavouriteProduct,
    SearchProduct,
    CategoryList,
    CategoryProductList,
    OrderUser,
    )

app_name = 'api'

urlpatterns = [
    path('product-list/', ProductList.as_view(), name='product-list'),
    path('trend-product-list/', TrendProductList.as_view(), name='trend-list'),
    path('favourite-product-list/', UserFavouriteProductList.as_view(), name='favourite-product-list'),
    path('favourite-product-list/?<productId>/', UserFavouriteProduct.as_view(), name='favourite-product'),
    path('product-detail/', ProductDetail.as_view(), name='product-detail'),
    path('search-product/', SearchProduct.as_view(), name='search-product'),
    path('category-list/', CategoryList.as_view(), name='category-list'),
    path('category-product-list/', CategoryProductList.as_view(), name='category-product-list'),
    path('order-user/', OrderUser.as_view(), name='order-user'),
]