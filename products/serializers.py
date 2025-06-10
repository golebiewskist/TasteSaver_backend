from rest_framework import serializers
from .models import Product, PantryPosition


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'barcode', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PantryPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryPosition
        fields = ['id', 'quantity', 'added_at', 'best_before']
        read_only_fields = ['id', 'added_at']


class CreatePantryPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryPosition
        fields = ['product', 'user', 'quantity', 'best_before']

    def create(self, validated_data):
        return PantryPosition.objects.create(**validated_data)