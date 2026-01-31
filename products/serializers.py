from rest_framework import serializers
from.models import Category,Products

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(
        source='category.name',
        read_only=True
    )
    class Meta:
        model=Products
        fields=[
            'id',
            'title',
            'description',
            'price',
            'image',
            'category',
            'category_name',
        ]