from django.db.models import fields
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import response
from rest_framework import authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from .serializers import (
    CategorySerializer, 
    OrderProductQuantitySerializer, 
    ProductSerializer, 
    MinimalProductSerializer, 
    OrderSerializer,
    AddressSerializer,
    StripeSerializer,
    OrderListSerializer,
    MobileCarouselSerializer,
    )
from . filters import ProductFilter, ProductFilterID, OrderProductFilterID
from .paginations import SearchProductPagination

from core.models import Address, FavouriteProduct, OrderProduct, Product, SpecialProduct, Category, Order, MobileCarousel

import stripe


# gets all product list (not used in anywhere)
class ProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

'''
Mobile carousel for advertisment at home screen
'''
class MobileCarouselList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = MobileCarousel.objects.all()
    serializer_class = MobileCarouselSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

# gets the all trend products
class TrendProductList(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = MinimalProductSerializer

    def get_queryset(self):
        special_product = get_object_or_404(SpecialProduct, title='trend')
        return special_product.products.all()

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

class ProductDetail(generics.GenericAPIView):
    def get(self, request, format=None):
        try:
            
            productId = int(request.query_params['productId'])
            product = Product.objects.get(id=productId)
        
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'productId': 'This field is required and must be numeric'} ,status=status.HTTP_400_BAD_REQUEST)
    

class UserFavouriteProduct(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    # if product id in facourite product list for that user response 200, or 404, 400
    def get(self, request, productId, format=None):
        try:
            if(productId in [product.id for product in FavouriteProduct.objects.get(user=request.user).products.all()]):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserFavouriteProductList(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # gets(response) the favourite products for requested user 
    def get(self, request, format=None):
        product_list = FavouriteProduct.objects.get(user=request.user).products.all()
        # if product id is given return response
            # return list of favourite product
        return Response(MinimalProductSerializer(product_list, many=True, context={'request': request}).data, status=status.HTTP_200_OK)

    # add product to favouriteProductlist or removes from favouriteProductlist
    # post method parameters are = ['id', 'action']
    def post(self, request):
        product_id = request.data['id']
        action = request.data['action'] # add or remove
        if action != 'add' and action != 'remove':
            return Response({'Invalid action' : 'Action must be either add or remove'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_id = int(product_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (product_id is not None):
            try:
                product = Product.objects.get(id=product_id)
                # FavouriteProduct object. get or create returns a tuple, (object, (true or false)) we need first element of this tuple
                favouriteProduct = FavouriteProduct.objects.get_or_create(user=request.user)[0]
                # product list for favourite product object
                favouriteProductList = favouriteProduct.products.all()
                # after this part there is no object does not exception error
                if product in favouriteProductList:
                    if action == 'add':
                        return Response({'Exist': 'Product is already in favourite list'}, status=status.HTTP_400_BAD_REQUEST)
                    elif action == 'remove':
                        favouriteProduct.products.remove(product)
                        return Response(status=status.HTTP_200_OK)
                else:
                    if action == 'add':
                        favouriteProduct.products.add(product)
                        return Response(status=status.HTTP_200_OK)
                    elif action == 'remove':
                        return Response({'Doesn\'t exist': 'Product is not in favourite list already'}, status=status.HTTP_400_BAD_REQUEST)

                
                #if product exist
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)


#searchs product for given query(title only)
class SearchProduct(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = MinimalProductSerializer
    filterset_class = ProductFilter
    pagination_class = SearchProductPagination

class CategoryList(generics.GenericAPIView):
    # gets category's descendants and itself by it's slug
    # query parameters = ['slug']
    def get(self, request, format=None):
        try:
            category_slug = request.query_params['slug']
            if(category_slug == 'root'):
                categories = Category.objects.filter(level__lt=1)
            else:
                categories = Category.objects.get(slug=category_slug).get_descendants(include_self=True)
            
            return Response(CategorySerializer(categories, many=True).data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CategoryProductList(APIView):
    pagination_class = SearchProductPagination
    
    # gets products for a category (includes it's descendants products)
    # than pagine it according to pagination class
    def get(self, request, format=None):
        try:
            category_slug = request.query_params['slug']

            product_list = Product.objects.filter(category__in=Category.objects.get(slug=category_slug).get_descendants(include_self=True))
            page = self.paginate_queryset(product_list)

            if page is not None:
                serializer = self.get_paginated_response(MinimalProductSerializer(page,many=True, context={'request': request}).data)
            else:
                serializer = MinimalProductSerializer(product_list, many=True, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    # these methods required for pagination to work
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator
    def paginate_queryset(self, queryset):
        
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset,
                   self.request, view=self)
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
            
class OrderUser(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            order = Order.objects.get_or_create(user=request.user, is_ordered=False)[0]
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# lists the all orders for requested user
class OrderListUser(generics.ListAPIView):
    authentication_classes =  (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_ordered=True)

class MinimalProduct(generics.ListAPIView):
    serializer_class = MinimalProductSerializer
    filterset_class = ProductFilterID
    queryset = Product.objects.all()


class OrderProductView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # this serializer is needed because of checking body parameters
    
    def get_object(self, id):
        try:
            return (OrderProduct.objects.get(id=id, user=self.request.user), False)
        except OrderProduct.DoesNotExist:
            return (Response(status=status.HTTP_404_NOT_FOUND), True)

    def put(self, request, id, format=None):
        orderProduct, error = self.get_object(id)
        if error:
            return orderProduct


        serializer = OrderProductQuantitySerializer(orderProduct, data=request.data)
         # if serializer is not valid (parameters are not included), it will raise an error
        # Example:if id is not included;  'id': This field is required.   error will occur 
        if serializer.is_valid(raise_exception=True):
            quantity = int(request.data['quantity'])
            # if quantity is greater than stock, user shouldn't be able to buy product which is out of limit.
            if(quantity > orderProduct.product.stock):
                return Response({'Stock': orderProduct.product.stock}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data)

    def delete(self, request, id, format=None):
        # body parameters
        
        orderProduct, error = self.get_object(id)
        if error:
            return orderProduct

        orderProduct.delete()

        return Response(status=status.HTTP_200_OK)

    def post(self, request, format=None):
        productId = request.data.get('productId')
        if(productId == None):
            return Response({'productId': 'This field is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=productId)
        
        # get active order for a user
        # if order does not exist create an order
        order, created = Order.objects.get_or_create(user=request.user, is_ordered=False)
        

        # if product in orderProduct list, no need to add it again because it already exists
        if product in [orderProduct.product for orderProduct in order.items.all()]:
            return Response({'Exist': 'Product already in order'}, status=status.HTTP_400_BAD_REQUEST)

        #create order product
        orderProduct = OrderProduct.objects.create(user=request.user, product=product, quantity=1)
        # add orderproduct to order
        order.items.add(orderProduct)
        order.save()

        return Response({'id': orderProduct.id}, status=status.HTTP_201_CREATED)


class AddressView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    # gets the address of requested user
    def get(self, request, format=None):
        addresses = Address.objects.filter(user=request.user)
        return Response(AddressSerializer(addresses, many=True).data, status=status.HTTP_200_OK)

    # creates a new address for a user
    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data ,status=status.HTTP_201_CREATED)

    # add address to order
    def put(self, request, format=None):
        address_id = request.data.get('id')
        if address_id is None:
            return Response({'id': 'This field is required'}, status=status.HTTP_400_BAD_REQUEST)

        address_id = int(address_id)

        # get address of requested user
        address = get_object_or_404(Address, id=address_id, user=request.user)

        # get order otherwise create
        order, created = Order.objects.get_or_create(user=request.user, is_ordered=False)

        # add address to order shipping and billing address
        # billing and shipping address might be different but I'm gonna leave it like this
        # because this is only for learning purpose
        order.billing_address = address
        order.shipping_address = address

        #save changes
        order.save()

        return Response(status=status.HTTP_200_OK)




class Stripe(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # it creates a stripe checkout session and returns a response which has url as a parameter.
    # this url redirects user to stripe checkout form (payment form) fro given orderProducts(line_items)
    def get(self, request, format=None):
        order = get_object_or_404(Order, user=request.user, is_ordered=False)
        line_items = []
        for orderProduct in order.items.all():
            
            line_items.append(
                {
                    'price_data': {
                        'currency': 'usd',
                            'unit_amount': int(orderProduct.product.price * 100),
                            'product_data': {
                                'name': orderProduct.product.title,
                                
                            },
                        },
                        'quantity': orderProduct.quantity,
                }
            )

        discounts = []
        if order.coupon:
            discounts.append({
                'coupon': order.coupon.key
            })

        # server IP address
        YOUR_DOMAIN = "http://192.168.0.108:8000/api"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={
                'order_pk': order.pk,
                'user_pk': self.request.user.id
            },
            mode='payment',
            discounts=discounts,
            success_url=YOUR_DOMAIN + '/stripe/success/',
            cancel_url=YOUR_DOMAIN + '/stripe/cancel/',
        )

        return Response(StripeSerializer(checkout_session).data, status=status.HTTP_200_OK)


from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.serializers import SocialLoginSerializer

"""
Makes google sign in verification
parameter: access_token or code
response: authentication token
"""
class Googlelogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/accounts/google/login/callback/'
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

        

