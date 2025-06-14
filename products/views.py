from datetime import timedelta, datetime

from django.utils import timezone
from translate import Translator
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Product, PantryPosition
from .serializers import ProductSerializer, PantryPositionSerializer


class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        data = serializer.validated_data.copy()
        language = self.request.headers.get('Language', 'en')

        # Tłumacz na angielski jeśli język źródłowy nie jest angielski
        if language != 'en':
            translator = Translator(from_lang=language, to_lang='en')

            if 'name' in data and data['name']:
                try:
                    data['name'] = translator.translate(data['name'])
                except Exception as e:
                    print(f"Name translation error: {str(e)}")

            if 'description' in data and data['description']:
                try:
                    data['description'] = translator.translate(data['description'])
                except Exception as e:
                    print(f"Description translation error: {str(e)}")

        barcode = data.get('barcode')
        if barcode and Product.objects.filter(barcode=barcode).exists():
            raise ValidationError({'barcode': 'Product with this barcode already exists.'})

        # Zapisz przetłumaczone dane
        serializer.save(**data)

    def get_queryset(self):
        return Product.objects.all()

    def list(self, request, *args, **kwargs):
        # Pobierz standardową odpowiedź
        response = super().list(request, *args, **kwargs)
        language = request.headers.get('Language', 'en')

        # Jeśli język angielski - zwróć bez zmian
        if language == 'en':
            return response

        # Utwórz synchroniczny tłumacz
        translator = Translator(to_lang=language)

        translated_data = []
        for product in response.data:
            translated = self.translate_product_data(product, translator)
            translated_data.append(translated)

        response.data = translated_data
        return response

    def translate_product_data(self, product_data, translator):
        """Tłumaczy pola produktu przy użyciu synchronicznego tłumacza"""
        try:
            translated = dict(product_data)

            if 'name' in translated and translated['name']:
                translated['name'] = translator.translate(translated['name'])

            if 'description' in translated and translated['description']:
                translated['description'] = translator.translate(translated['description'])

            return translated

        except Exception as e:
            print(f"Translation error: {str(e)}")
            return product_data


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'barcode'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        language = request.headers.get('Language', 'en')
        if language != 'en':
            data = self.translate_product_data(data, language)

        return Response(data)

    def translate_product_data(self, product_data, language):
        """Tłumaczy pola produktu na język docelowy"""
        try:
            translator = Translator(to_lang=language)
            translated = dict(product_data)

            if 'name' in translated and translated['name']:
                translated['name'] = translator.translate(translated['name'])

            if 'description' in translated and translated['description']:
                translated['description'] = translator.translate(translated['description'])

            return translated

        except Exception as e:
            print(f"Translation error: {str(e)}")
            return product_data


class ProductDetailByIDView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        language = request.headers.get('Language', 'en')
        if language != 'en':
            data = self.translate_product_data(data, language)

        return Response(data)

    def translate_product_data(self, product_data, language):
        """Tłumaczy pola produktu na język docelowy"""
        try:
            translator = Translator(to_lang=language)
            translated = dict(product_data)

            if 'name' in translated and translated['name']:
                translated['name'] = translator.translate(translated['name'])

            if 'description' in translated and translated['description']:
                translated['description'] = translator.translate(translated['description'])

            return translated

        except Exception as e:
            print(f"Translation error: {str(e)}")
            return product_data


class PantryPositionsListView(generics.ListAPIView):
    serializer_class = PantryPositionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PantryPosition.objects.filter()#user=self.request.user)

class PantryPositionDetailView(generics.ListAPIView):
    serializer_class = PantryPositionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    lookup = 'barcode'

    def get_queryset(self):
        barcode = self.kwargs['barcode']
        try:
            product = Product.objects.filter(barcode=barcode).first()
        except Product.DoesNotExist:
            raise NotFound(f"Product with barcode {barcode} does not exist")

        try:
            return PantryPosition.objects.filter(
                #user=self.request.user,
                product=product
            )
        except PantryPosition.DoesNotExist:
            raise NotFound("Pantry position not found for this product")


class PantryPositionCreateView(generics.CreateAPIView):
    serializer_class = PantryPositionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        barcode = self.request.data.get('barcode')
        best_before = self.request.data.get('best_before')
        quantity = self.request.data.get('quantity')

        if not barcode:
            raise ValidationError({'barcode': 'This field is required'})

        if not quantity:
            raise ValidationError({'quantity': 'This field is required'})

        try:
            product = Product.objects.filter(barcode=barcode).first()
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