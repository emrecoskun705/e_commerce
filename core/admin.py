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
    Coupon,
    Rate,
    ProductRate,
    SpecialProduct,
    FavouriteProduct,
    MobileCarousel,
)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
    readonly_fields = ('id',)
    class Meta:
        model = Product

admin.site.register(ProductImage)


""" CATEGORY """
admin.site.register(Category, MPTTModelAdmin)

admin.site.register(Address)

admin.site.register(Payment)

admin.site.register(UserProfile)

admin.site.register(Refund)

admin.site.register(Coupon)

admin.site.register(MobileCarousel)


admin.site.register(FavouriteProduct)

@admin.register(SpecialProduct)
class SpecialProductAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('user','rate')

@admin.register(ProductRate)
class ProductRateAdmin(admin.ModelAdmin):
    list_display = ('product',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ref_code')
