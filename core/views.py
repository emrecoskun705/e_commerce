from django.core.exceptions import ObjectDoesNotExist
from django.http import request
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from .models import Order, Product, Category, OrderProduct
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

class HomeView(ListView):
    model = Product
    paginate_by = 20
    template_name = 'index.html'
    ordering = ['-id']


    #This part filters categories by at the top of every trees which are roots
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(level__lt=1)
        return context

class ProductDetailView(DetailView):
    """Product detail view, it finds prdocut by slug in core.urls"""
    model = Product
    template_name = 'product_detail.html'

class CartView(View):
    def get(self, *args, **kwargs):
        # if user is authenticated show product items
        if self.request.user.is_authenticated:
            try:
                order = Order.objects.get(user=self.request.user, is_ordered=False)
                context = {
                    'order': order
                }
                return render(self.request, 'cart.html', context)
            except ObjectDoesNotExist:
                messages.warning(self.request, 'No products in here')
                return redirect('/')
        else:
            # if user is not authenticated show empty cart
            context = {}
            return render(self.request, 'cart.html', context)

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderProduct.objects.get_or_create(product=product,user=request.user)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    #if there is an order there are two options
    #1. update quantity
    #2. add order_product to order
    if order_qs.exists():
        order = order_qs[0]
        #check for order item
        if order.items.filter(product__slug=product.slug).exists():
            if order_product.quantity+1 > order_product.product.stock:
                messages.warning(request, 'Product stock is not eneough')
                return redirect('core:cart')
            order_product.quantity += 1
            order_product.save()
            messages.info(request, "Prodcut quantity updated.")
            return redirect('core:cart')
        else:
            order.items.add(order_product)
            messages.info(request, 'Product was added to your cart')
            return redirect('core:cart')
    else:
        #if order isn' exists
        date = timezone.now()
        new_order = Order.objects.create(user=request.user, order_date=date)
        new_order.items.add(order_product)
        messages.info(request, 'Product was added to your cart')
        return redirect('core:cart')

@login_required
def remove_product_from_cart(request, slug):
    """
     1. find the product
     2. find orderProduct according to user and product
     3. Locate the order for orderProduct
     4. Remove it from order
    """
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(product=product, user=request.user, is_ordered=False)[0]
            order.items.remove(order_product)
            order_product.delete()
            messages.info(request, 'Product has been removed')
            return redirect('core:cart')
        else:
            messages.info(request, "This item is not in your cart")
            return redirect('core:product-detail', slug=slug)
    else:
        messages.info(request, "Order isn't created")
        return product.get_absolute_url()

@login_required
def remove_one_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(product=product,user=request.user,is_ordered=False)[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
            else:
                order.items.remove(order_product)
            messages.info(request, "Product has been updated.")
            return redirect("core:cart")
        else:
            messages.info(request, "Product is not in your cart.")
            return redirect("core:product-detail", slug=slug)
    else:
        messages.info(request, "Your cart is empty")
        return redirect("core:product-detail", slug=slug)

class CheckoutView(LoginRequiredMixin, View):
    """
    Now it is only for visuality,
    TODO: Checkout part will be in here
    """
    login_url = '/accounts/login/'
    def get(self, *args, **kwargs):
        return render(self.request, 'checkout.html')