from rest_framework import serializers
from .models import Product, PantryPosition


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [ 'name', 'description', 'barcode']

class PantryPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PantryPosition
        fields = [ 'product', 'quantity', 'best_before']
        read_only_fields = ['product']