from django.db.models import fields
from django_filters import rest_framework as filters
from django_filters import ModelChoiceFilter
from mptt.forms import TreeNodeChoiceField
from core.models import Product


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(required=True, lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('title',)

class CategoryProductFilter(filters.FilterSet):
    slug = filters.CharFilter(required=True, lookup_expr='exact')

    class Meta:
        model = Product
        fields = ('category__slug',)
    