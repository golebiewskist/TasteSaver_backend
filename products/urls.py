from django.urls import path
from . import views
from .views import GetOldPantryPositionsView, RecipeSuggestionView, PantryPositionsWithProductView

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<str:barcode>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('pantry-positions/', views.PantryPositionsListView.as_view(), name='pantry-position-list'),

    path('pantry-positions/get/<str:barcode>/', views.PantryPositionDetailView.as_view(), name='pantry-position-detail'),
    path('pantry-positions/add/', views.PantryPositionCreateView.as_view(), name='pantry-position-add'),

    path('pantry-positions/remove/<str:barcode>/', views.RemoveQuantityFromPantryView.as_view(), name='pantry-position-remove'),

    path('pantry-positions/old/', GetOldPantryPositionsView.as_view(), name='pantry-positions-old'),
    path('pantry-positions/recipe/', RecipeSuggestionView.as_view(), name='pantry-positions-recipe'),
    path('pantry-positions-with-product/', PantryPositionsWithProductView.as_view(), name='pantry-positions-with-product'),
]