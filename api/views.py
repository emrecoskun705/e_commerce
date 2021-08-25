from django.db.models import fields
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics

from .serializers import CategorySerializer, ProductSerializer, MinimalProductSerializer, OrderSerializer, OrderProductSerializer
from . filters import ProductFilter, ProductFilterID, OrderProductFilterID
from .paginations import SearchProductPagination

from core.models import FavouriteProduct, OrderProduct, Product, SpecialProduct, Category, Order

# gets all product list (not used in anywhere)
class ProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

# gets the all trend products
class TrendProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = SpecialProduct.objects.filter(title='trend')[0].products.all()
    serializer_class = MinimalProductSerializer

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
    # if product id in facourite product list for that user response 200, or 404, 400
    def get(self, request, format=None):
        try:
            productId = int(request.query_params['productId'])
            if(productId in [product.id for product in FavouriteProduct.objects.get(user=request.user).products.all()]):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserFavouriteProductList(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    # gets(response) the favourite products for requested user 
    def get(self, request, format=None):
        product_list = FavouriteProduct.objects.get(user=request.user).products.all()
        
        # if product id is given return response
        try:
            # this query parameter is optional, for only getting the specific product is in that favaourite product list
            productId = int(request.query_params['productId'])
            if productId in [product.id for product in product_list]:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            # return list of favourite product
            return Response(ProductSerializer(product_list, many=True).data)

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

    def get(self, request, format=None):
        try:
            order = Order.objects.get_or_create(user=request.user, is_ordered=False)[0]
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class MinimalProduct(generics.ListAPIView):
    serializer_class = MinimalProductSerializer
    filterset_class = ProductFilterID
    queryset = Product.objects.all()


class OrderProductView(APIView):
    authentication_classes = (TokenAuthentication,)
    # this serializer is needed because of checking body parameters
    
    def get_object(self, id):
        try:
            return OrderProduct.objects.get(id=id, user=self.request.user)
        except OrderProduct.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id, format=None):
        orderProduct = self.get_object(id)
        serializer = OrderProductSerializer(orderProduct, data=request.data)
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
        
        orderProduct = self.get_object(id)
        orderProduct.delete()

        return Response(status=status.HTTP_200_OK)