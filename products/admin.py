from django.contrib import admin
from .models import Product, PantryPosition

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode']
    search_fields = ['name', 'barcode']

@admin.register(PantryPosition)
class PantryPositionAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'best_before']
    list_filter = ['user', 'best_before']
    search_fields = ['product__name', 'user__username']
    raw_id_fields = ['product', 'user']