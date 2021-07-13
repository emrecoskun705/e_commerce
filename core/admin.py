from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import (
    Product,
    ProductImage,
    Category
)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]

    class Meta:
        model = Product

admin.site.register(ProductImage)


""" CATEGORY """
admin.site.register(Category, MPTTModelAdmin)