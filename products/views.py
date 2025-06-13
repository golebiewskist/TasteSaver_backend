from datetime import timedelta
from random import betavariate

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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

class PantryPositionDetailView(generics.RetrieveAPIView):
    serializer_class = PantryPositionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'barcode'

    def get_queryset(self):
        return PantryPosition.objects.filter(user=self.request.user)


class PantryPositionCreateView(generics.CreateAPIView):
    serializer_class = PantryPositionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        barcode = self.request.data.get('barcode')
        best_before = self.request.data.get('best_before')
        quantity = self.request.data.get('quantity', 1)

        if not barcode:
            raise ValidationError({'barcode': 'This field is required'})

        try:
            product = Product.objects.get(barcode=barcode)
        except Product.DoesNotExist:
            raise NotFound(f"Product with barcode {barcode} does not exist")

        
        existing_position = PantryPosition.objects.filter(
            user=self.request.user,
            product=product,
            best_before=best_before
        ).first()

        if existing_position:
            existing_position.quantity += int(quantity)
            existing_position.save()
            serializer.instance = existing_position
        else:
            serializer.save(
                user=self.request.user,
                product=product,
                quantity=quantity,
                best_before=best_before
            )


class RemoveQuantityFromPantryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, barcode):

        quantity_to_remove = request.data.get('quantity', 1)
        best_before = request.data.get('best_before')

        try:
            quantity_to_remove = int(quantity_to_remove)
        except (TypeError, ValueError):
            return Response(
                {"error": "Quantity must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity_to_remove <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )


        try:
            product = Product.objects.get(barcode=barcode)
        except Product.DoesNotExist:
            return Response(
                {"error": f"Product with barcode {barcode} not found"},
                status=status.HTTP_404_NOT_FOUND
            )


        try:
            position = PantryPosition.objects.get(
                user=request.user,
                product=product,
                best_before=best_before
            )
        except PantryPosition.DoesNotExist:
            return Response(
                {"error": "You don't have this product in your pantry"},
                status=status.HTTP_404_NOT_FOUND
            )

        if position.quantity < quantity_to_remove:
            return Response(
                {"error": f"Not enough quantity. You only have {position.quantity}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        position.quantity -= quantity_to_remove
        if position.quantity <= 0:
            position.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            position.save()
            serializer = PantryPositionSerializer(position)
            return Response(serializer.data, status=status.HTTP_200_OK)


class GetOldPantryPositionsView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PantryPositionSerializer

    def get_queryset(self):
        today = timezone.now().date() + timedelta(days=10)
        return PantryPosition.objects.filter(user=self.request.user, best_before__lt=today ).order_by('-best_before')