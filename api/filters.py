from django.db.models import fields
from django_filters import rest_framework as filters
from django_filters import ModelChoiceFilter
from mptt.forms import TreeNodeChoiceField
from core.models import Product, OrderProduct


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(required=True, lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('title',)

class ProductFilterID(filters.FilterSet):
    id = filters.CharFilter(required=True)

    class Meta:
        model = Product
        fields = ('id',)

class OrderProductFilterID(filters.FilterSet):
    id = filters.CharFilter(required=True)
    
    class Meta:
        model = OrderProduct
        fields = ('id',)
    