from django.db import models
from rest_framework import fields, serializers
from core.models import Product, Category, Order, OrderProduct, Address, Payment, MobileCarousel


class StripeSerializer(serializers.Serializer):
    url = serializers.CharField()

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ('user',)
    


# to make a order product POST request
class OrderProductQuantitySerializer(serializers.ModelSerializer):
    # these parameters are required so user must enter these parameters
    quantity = serializers.IntegerField(required=True)
    class Meta:
        model = OrderProduct
        fields = ('quantity',)


class MobileCarouselSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MobileCarousel
        fields = ('image',)
    #get full path
    def get_image(self, product):
        request = self.context.get('request')
        image = product.image.url
        return request.build_absolute_uri(image)

class MinimalProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
            'discount_price',
            'image',
        ]

    #get full path
    def get_image(self, product):
        request = self.context.get('request')
        image = product.image.url
        return request.build_absolute_uri(image)

class OrderProductSerializer(serializers.ModelSerializer):
    product = MinimalProductSerializer()

    class Meta:
        model = OrderProduct
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('amount',)

class OrderListSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    items = OrderProductSerializer(many=True)
    class Meta:
        model = Order
        exclude = ('user', 'timestamp', 'is_ordered', 'shipping_address', 'billing_address')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('items',)
        depth = 1

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id',
                'title',
                'price',
                'discount_price',
                'slug',
                'description',
                'image',
                'stock',
                'images',
        ]
        # when we use depth = 1, now we can reach the fields of images(ImageProduct object)
        depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'parent',
        ]
