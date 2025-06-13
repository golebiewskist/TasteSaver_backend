from rest_framework import serializers
from .models import Product, PantryPosition


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'barcode']
        read_only_fields = ['id']

class PantryPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryPosition
        fields = ['id', 'quantity', 'best_before']
        read_only_fields = ['id']