from rest_framework import serializers
from .models import Product, PantryPosition


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'barcode']
        read_only_fields = ['id']

class PantryPositionSerializer(serializers.ModelSerializer):
    barcode = serializers.CharField(write_only=True)

    class Meta:
        model = PantryPosition
        fields = [ 'product', 'quantity', 'best_before', 'barcode']
        read_only_fields = ['product']
        extra_kwargs = {
            'product': {'required': False}
        }