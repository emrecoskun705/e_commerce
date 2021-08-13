from rest_framework import fields, serializers
from core.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title',
                'price',
                'discount_price',
                'slug',
                'description',
                'image',
                'stock',
            
        ]
