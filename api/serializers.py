from rest_framework import fields, serializers
from core.models import Product, ProductImage

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
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
            'discount_price',
            'image',
        ]
