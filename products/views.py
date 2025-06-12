from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Product, PantryPosition
from .serializers import ProductSerializer, PantryPositionSerializer


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        barcode = serializer.validated_data.get('barcode')

        if Product.objects.filter(barcode=barcode).exists():
            raise ValidationError({'barcode': 'Product with this barcode already exists.'})

        serializer.save()


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'barcode'


class PantryPositionsListView(generics.ListAPIView):
    serializer_class = PantryPositionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PantryPosition.objects.filter(user=self.request.user)