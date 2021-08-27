from django.db import models
from rest_framework import fields, serializers
from core.models import Product, Category, Order, OrderProduct, Address


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

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'parent',
        ]
