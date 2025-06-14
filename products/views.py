from datetime import timedelta, datetime

import requests
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
from .serializers import ProductSerializer, PantryPositionSerializer, PantryPositionWithProductSerializer


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
        product = self.request.data.get('product')
        best_before = self.request.data.get('best_before')
        quantity = self.request.data.get('quantity')

        if not product:
            raise ValidationError({'product': 'This field is required'})

        if not quantity:
            raise ValidationError({'quantity': 'This field is required'})

        try:
            product = Product.objects.filter(barcode=product).first()
        except Product.DoesNotExist:
            raise NotFound(f"Product with barcode {product} does not exist")

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
        date = timezone.now().date() + timedelta(days=10)
        return PantryPosition.objects.filter(
            user=self.request.user,
            best_before__lt=date
        ).order_by('-best_before')


class RecipeSuggestionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        language = self.request.headers.get('Language', 'en')

        positions = PantryPosition.objects.filter(
            user=request.user,
        ).order_by('best_before')

        if not positions:
            return Response(
                {"detail": "No ingredients found in your pantry"},
                status=status.HTTP_404_NOT_FOUND
            )

        closest_position = positions[0]
        ingredient_name = closest_position.product.name

        try:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/filter.php",
                params={'i': ingredient_name},
                timeout=5  # 5 sekund timeout
            )

            if response.status_code != 200:
                return Response(
                    {"detail": "Failed to fetch recipes from TheMealDB"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            data = response.json()
            meals = data.get('meals', [])

            if not meals:
                return Response(
                    {"detail": f"No recipes found for {ingredient_name}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            first_recipe = meals[0]

            recipe_id = first_recipe.get('idMeal')

            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/lookup.php",
                params = {'i': recipe_id},
                timeout = 5
            )

            data = response.json()
            meals = data.get('meals', [])
            recipe = meals[0]

            recipe_name = recipe.get('strMeal')

            instructions = recipe.get('strInstructions')

            if language == 'en':
                return Response({
                    'recipe_name': recipe_name,
                    'instructions': instructions
                })

            else:
                translator = Translator(to_lang=language)
                recipe_name = translator.translate(recipe_name)

                instructions_trans = ""
                if instructions:
                    chunk_size = 500
                    chunks = [
                        instructions[i:i + chunk_size]
                        for i in range(0, len(instructions), chunk_size)
                    ]

                    for chunk in chunks:
                        try:
                            translated_chunk = translator.translate(chunk)
                            instructions_trans += translated_chunk + " "
                        except Exception:
                            instructions_trans += chunk + " "


                return Response({
                    'recipe_name': recipe_name,
                    'instructions': instructions_trans
                })


        except requests.exceptions.RequestException as e:
            return Response(
                {"detail": f"API request failed: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class PantryPositionsWithProductView(generics.ListAPIView):
    serializer_class = PantryPositionWithProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PantryPosition.objects.filter(user=self.request.user).select_related('product')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        language = request.headers.get('Language', 'en')

        if language == 'en':
            return response

        translator = Translator(to_lang=language)
        translated_data = []

        for position in response.data:
            try:
                # Stwórz kopię danych
                translated = dict(position)

                # Tłumacz dane produktu
                if 'product' in translated and translated['product']:
                    product = translated['product']

                    if 'name' in product and product['name']:
                        product['name'] = translator.translate(product['name'])

                    if 'description' in product and product['description']:
                        product['description'] = translator.translate(product['description'])

                    translated['product'] = product

                translated_data.append(translated)

            except Exception as e:
                print(f"Translation error: {str(e)}")
                translated_data.append(position)

        response.data = translated_data
        return response