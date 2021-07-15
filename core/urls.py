from django.urls import path
from .views import (
    HomeView,
    ProductDetailView,
    CartView,
    CheckoutView,
    add_to_cart,
    remove_product_from_cart,
    remove_one_product
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<slug:slug>/', add_to_cart, name='add-to-cart'),
    path('remove-product/<slug:slug>/', remove_product_from_cart, name='remove-product'),
    path('remove-one-product/<slug:slug>/', remove_one_product, name='remove-one-product'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]