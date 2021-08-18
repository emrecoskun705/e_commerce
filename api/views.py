from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication

from .serializers import ProductSerializer
from rest_framework import generics

from core.models import FavouriteProduct, Product, SpecialProduct

# gets all product list (not used in anywhere)
class ProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

# gets the all trend products
class TrendProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = SpecialProduct.objects.filter(title='trend')[0].products.all()
    serializer_class = ProductSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)


class FavouriteProductList(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)

    # gets(response) the favourite products for requested user 
    def get(self, request, format=None):
        product_list = [product for product in FavouriteProduct.objects.get(user=request.user).products.all()]
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
            
            



    