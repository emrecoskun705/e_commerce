from django.db.models import fields
from django_filters import rest_framework as filters
from core.models import Product


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(required=True, lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('title',)
    