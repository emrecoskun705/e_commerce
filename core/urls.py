from django.urls import path
from .views import (
    HomeView,
    ProductDetailView,
    CartView,
    CheckoutView,
    SuccessView,
    CancelView,
    PromoCodeView,
    OrderListView,
    RefunRequestView,
    RefundListView,
    SearchView,
    #PaymentView,
    add_to_cart,
    remove_product_from_cart,
    remove_one_product,
    stripe_webhook
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
    path('promo-code/', PromoCodeView.as_view(), name='promo-code'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('refund/<str:ref_code>/', RefunRequestView.as_view(), name='refund'),
    path('refund-list/', RefundListView.as_view(), name='refund-list'),
    path('search/', SearchView.as_view(), name='search'),
    path('search/<str:category>/', SearchView.as_view(), name='search'),
    #path('payment/', PaymentView.as_view(), name='payment'),
]