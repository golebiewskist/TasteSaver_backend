from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<string:barcode>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('pantry-positions/', views.PantryPositionsListView.as_view(), name='pantry-position-create'),
]