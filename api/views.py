from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from .serializers import ProductSerializer
from rest_framework import generics

from core.models import Product, SpecialProduct

class ProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

class TrendProductList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = SpecialProduct.objects.filter(title='trend')[0].products.all()
    serializer_class = ProductSerializer

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)
    