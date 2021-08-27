from django.urls.conf import include, path
from core.forms import CheckoutForm, CouponForm, RefundForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import request, JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Payment, Product, Category, OrderProduct, Address, Coupon, Refund
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import stripe
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))



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

class SearchView(View):
    def get(self, *args, **kwargs):
        """
        Simple search engine for searching by category and product name
        """
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        if search:
            #filters products if it contains search attribute
            product_list = Product.objects.filter(title__icontains=search)
            context = {
                'product_list': product_list
            }
        elif category:
            #category = get_object_or_404(Category, slug=category)
            #print(category)
            try:
                # Collects all the product for a category including their descendants
                product_list = Product.objects.filter(category__in=Category.objects.get(slug=category).get_descendants(include_self=True))
            except ObjectDoesNotExist:
                messages.warning('There is no category like this')
                return redirect('/')
            
            context = {
                'product_list': product_list
            }

        return render(self.request, 'search.html', context)
            

class OrderListView(LoginRequiredMixin ,ListView):
    template_name = 'orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        #list by the user
        queryset = Order.objects.filter(user=self.request.user, is_ordered=True).order_by('-order_date')
        return queryset
    
    
    
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
                #if cart is empty no need to show cart view
                if order.items.count() < 1:
                    messages.warning(self.request, 'No products in here')
                    return redirect('/')
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
    order_product, created = OrderProduct.objects.get_or_create(product=product,user=request.user, is_ordered=False)
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
        
        new_order = Order.objects.create(user=request.user)
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
            print(OrderProduct.objects.filter(product=product,user=request.user,is_ordered=False))
            order_product = OrderProduct.objects.filter(product=product,user=request.user,is_ordered=False)[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
            else:
                order.items.remove(order_product)
                order_product.delete()
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
        #first we need to catch the user for __init__, then fetch the post
        form = CheckoutForm(self.request.user, self.request.POST)
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

            #shipping address informations
            address_title = form.cleaned_data.get('shipping_address_title')
            country = form.cleaned_data.get('country')
            province = form.cleaned_data.get('province')
            zip = form.cleaned_data.get('zip')
            address_detail = form.cleaned_data.get('address_detail')

            #billing address informations
            billing_address_title = form.cleaned_data.get('billing_address_title')
            billing_country = form.cleaned_data.get('billing_country')
            billing_province = form.cleaned_data.get('billing_province')
            billing_zip = form.cleaned_data.get('billing_zip')
            billing_address_detail = form.cleaned_data.get('billing_address_detail')

            #shipping address choice fields values
            shipping_address = form.cleaned_data.get('shipping_address')
            billing_address = form.cleaned_data.get('billing_address')
            # if addresses are not none, it means that address has been selected
            if shipping_address != "None":              
                shipping_address = get_object_or_404(Address, pk=int(shipping_address))
            else:
                shipping_address = None

            if billing_address != "None":
                billing_address = get_object_or_404(Address, pk=int(billing_address))
            else:
                billing_address = None

            # check all fields then update the order
            if (shipping_address is not None) and (billing_address is not None):
                order.shipping_address = shipping_address
                order.billing_address = billing_address
                order.save()
            elif (shipping_address is not None) and (form.cleaned_data.get('same_billing_address')):
                order.shipping_address = shipping_address
                order.billing_address = shipping_address
                order.save()
            elif (billing_address is not None) and (form.cleaned_data.get('same_billing_address')):
                order.shipping_address = billing_address
                order.billing_address = billing_address
                order.save()
            elif shipping_address is not None:
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
                    order.shipping_address = shipping_address
                    order.billing_address = address_billing
                    order.save()
                else:
                    messages.warning(self.request, "Please enter a valid address")
                    return redirect('core:checkout')
            elif billing_address is not None:
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
                    order.shipping_address = address
                    order.billing_address = billing_address
                    order.save()
                else:
                    messages.warning(self.request, "Please enter a valid address")
                    return redirect('core:checkout')
            else:

                #if they are not empty it will continue for shipping address
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
                    #return redirect('core:payment')
                else:
                    # if it is not same billing address
                    
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

            #stripe
            YOUR_DOMAIN = "http://127.0.0.1:8000"
            #Store the product items in line items list
            line_items = []
            for order_item in order.items.all():
                line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(order_item.product.price * 100),
                            'product_data': {
                                'name': order_item.product.title,
                                
                            },
                        },
                        'quantity': order_item.quantity,
                    })

            print(line_items)

            discounts = []
            if order.coupon:
                discounts.append({
                    'coupon': order.coupon.key
                })
            #create checkout session,
            #Put order_pk and user_pk in metadata. Because we need to know which user is request for payment
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                metadata={
                    'order_pk': order.pk,
                    'user_pk': self.request.user.pk
                },
                mode='payment',
                discounts=discounts,
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )
            return redirect(checkout_session.url, code=303)
            

class RefunRequestView(LoginRequiredMixin, View):
    def get(self, request, ref_code, *args, **kwargs):
        order = get_object_or_404(Order, ref_code=ref_code, user=self.request.user)

        if order.order_date and (datetime.now(tz=timezone.utc) - order.order_date).days > 14:
            messages.warning(self.request, 'You can not refund after 14 days')
            return redirect('/')
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'refund.html', context)
    
    def post(self, request,  ref_code, *args, **kwargs):
        order = get_object_or_404(Order, ref_code=ref_code, user=self.request.user)
        if order.order_date and (datetime.now(tz=timezone.utc) - order.order_date).days > 14:
            messages.warning(self.request, 'You can not refund after 14 days')
            return redirect('/')
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            reason = form.cleaned_data.get('reason')
            email = form.cleaned_data.get('email')

            #update bool refun request for order
            order.is_refund_requested = True
            order.save()

            #create refund request
            refund = Refund()
            refund.order = order
            refund.reason = reason
            refund.email = email
            refund.save()

            
            send_mail(
                subject="Refund Request",
                message="Refund request has been received.",
                recipient_list=[email],
                from_email="emre@test.com"
            )

            messages.info(self.request, 'We will be contact you, soon')
            #Redirect to refund lists
            return redirect('core:refund-list')
        messages.warning(self.request, 'Please give valid form inputs')
        # Redirects the same page
        return redirect(self.request.META.get('HTTP_REFERER'))

class RefundListView(LoginRequiredMixin, ListView):
    """
    Refund List for requested user
    """
    template_name = 'refund-list.html'
    context_object_name = 'refunds'

    def get_queryset(self):
        #list by the user
        queryset = Refund.objects.filter(order__user=self.request.user).order_by('-timestamp')
        return queryset


class PromoCodeView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            promo_code = form.cleaned_data.get('promo_code')
            order = get_object_or_404(Order, user=self.request.user, is_ordered=False)
            #get coupon
            try:
                coupon = Coupon.objects.get(key=promo_code)
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Coupon successfully added")
                return redirect('core:checkout')
            except ObjectDoesNotExist:
                messages.info(self.request, 'This coupon does not exist')
                return redirect('core:checkout')


class SuccessView(TemplateView):
    """
        If payment is successful
    """
    template_name = "snippets/success.html"

class CancelView(TemplateView):
    """
        If payment is canceled
    """
    template_name = "snippets/cancel.html"
    
@csrf_exempt
def stripe_webhook(request):
    '''
        This part will activate when user submits the payment in stripe website
        Strip webhook must be working for catching requests!!!!
    '''
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_KEY #actually this is enpoint secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # if it is true, payment was successful 
    if event['type'] == 'checkout.session.completed':
        #session contains payment informations
        session = event['data']['object']
        customer_email = session['customer_details']['email']

        order_pk = session['metadata']['order_pk']
        user_pk = session['metadata']['user_pk']

        order = get_object_or_404(Order, pk=order_pk)
        user = get_object_or_404(User, pk=user_pk)

        # create payment and update values then save
        payment = Payment()
        payment.stripe_payment_intent = session['payment_intent']
        payment.user = user
        payment.amount = session['amount_total'] / 100
        payment.save()

        # all order items are ordered now, so change the value to True then save all of them
        order_items = order.items.all()
        order_items.update(is_ordered=True)
        for item in order_items:
            item.product.stock -= item.quantity
            item.product.save()
            item.save()
        
        # order is finished
        order.is_ordered = True
        order.payment = payment
        order.ref_code = create_ref_code()
        order.order_date = datetime.now(tz=timezone.utc)
        order.save()

        #send mail to customer, but it is now only works in console 
        #TODO - in production change mail backends
        send_mail(
            subject="Successful Order",
            message="Your order has been completed.",
            recipient_list=[customer_email],
            from_email="emre@test.com"
        )

    # Passed signature verification
    return HttpResponse(status=200)
        