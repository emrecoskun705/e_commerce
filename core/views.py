from core.forms import CheckoutForm, CouponForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import request
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from .models import Order, Product, Category, OrderProduct, Address
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
    login_url = '/accounts/login/'
    def get(self, *args, **kwargs):
        order = get_object_or_404(Order, user=self.request.user, is_ordered=False)
        checkout_form = CheckoutForm(self.request.user)
        coupon_form = CouponForm()
        context = {
            'order': order,
            'checkout_form': checkout_form,
            'coupon_form': coupon_form
        }
        return render(self.request, 'checkout.html', context)
    def post(self, *args, **kwargs):
        """
        We get checkout form from post request,
        if form and form fields are valid for address and order model,
        we will continue to payment part
        """
        form = CheckoutForm(self.request.POST or None)
        order = get_object_or_404(Order, user=self.request.user, is_ordered=False)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            if first_name and last_name:
                order.first_name = first_name
                order.last_name = last_name
            else:
                messages.warning(self.request, 'Please enter your name')
                return redirect('core:checkout')
            address_title = form.cleaned_data.get('shipping_address_title')
            country = form.cleaned_data.get('country')
            province = form.cleaned_data.get('province')
            zip = form.cleaned_data.get('zip')
            address_detail = form.cleaned_data.get('address_detail')
            #if they are not empty it will continue
            if address_title and country and province and zip and address_detail:
                address = Address(
                    user = self.request.user,
                    address_title = address_title,
                    country = country,
                    province = province, 
                    zip = zip,
                    detail = address_detail
                )

                address.save()
            else:
                messages.warning(self.request, "Please enter a valid address")
                return redirect('core:checkout')

            #if same billing address is true, shipping and billing address will be same
            if form.cleaned_data.get('same_billing_address'):
                order.shipping_address = address
                order.billing_address = address

                order.save()
                return redirect('core:payment')
            else:
                # if it is not same billing address
                billing_address_title = form.cleaned_data.get('billing_address_title')
                billing_country = form.cleaned_data.get('billing_country')
                billing_province = form.cleaned_data.get('billing_province')
                billing_zip = form.cleaned_data.get('billing_zip')
                billing_address_detail = form.cleaned_data.get('billing_address_detail')
                if billing_address_title and billing_country and billing_province and billing_zip and billing_address_detail:

                    address_billing = Address(
                        user = self.request.user,
                        address_title = billing_address_title,
                        country = billing_country,
                        province = billing_province, 
                        zip = billing_zip,
                        detail = billing_address_detail
                    )

                    address_billing.save()

                    order.shipping_address = address
                    order.billing_address = address_billing

                    order.save()
                else:
                    messages.warning(self.request, "Please enter a valid billing address")
                    return redirect('core:checkout')
                return redirect('core:payment')

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')