from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django.contrib.auth.decorators import login_required

"""
Django allauth does not work for admin site authentication, so it may be brute forced by attackers.
Prevent this, we change the admin site login method to django-allauth login method
"""
admin.site.login = login_required(admin.site.login)

from .models import (
    Product,
    ProductImage,
    Category,
    OrderProduct,
    Order,
    Address,
    Payment,
    UserProfile,
    Refund,
    Coupon
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

admin.site.register(OrderProduct)


admin.site.register(Address)

admin.site.register(Payment)

admin.site.register(UserProfile)

admin.site.register(Refund)

admin.site.register(Coupon)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ref_code')
