
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    TagSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(
        Prefetch('favorite_users', queryset=User.objects.only('id')),
        Prefetch('shopping_cart_users', queryset=User.objects.only('id'))
    )
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    http_method_names = (
        'post', 'patch', 'get', 'delete', 'head', 'options'
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        self.save_recipe(serializer)

    def perform_update(self, serializer):
        self.save_recipe(serializer)

    def save_recipe(self, serializer):
        """Универсальная функция для создания и обновления."""
        ingredients = serializer.validated_data.pop('recipe_ingredients')
        tags = serializer.validated_data.pop('tags')
        # Создаём или обновляем рецепт (пока без ингредиентов и тегов).
        recipe = serializer.save()
        # Создаём или обновляем ингредиенты.
        if recipe.recipe_ingredients.exists():
            recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
        # Создаём или обновляем теги.
        recipe.tags.set(tags)
        return recipe

    @action(('get',), detail=True, url_path='get-link')
    def get_short_link(self, request, pk):
        return Response({
            'short-link': request.build_absolute_uri(
                f'/s/{self.get_object().id}'
            )
        })

    @action(('post',), detail=True, url_path='shopping_cart')
    def add_to_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.shopping_cart_users.filter(id=request.user.id).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.shopping_cart_users.add(request.user)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe.shopping_cart_users.filter(id=request.user.id).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.shopping_cart_users.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('post',), detail=True, url_path='favorite')
    def add_to_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.favorite_users.filter(id=request.user.id).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.favorite_users.add(request.user)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe.favorite_users.filter(id=request.user.id).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.favorite_users.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        # Регистрация шрифта.
        pdfmetrics.registerFont(
            TTFont(
                'OpenSans',
                settings.BASE_DIR / 'fonts/OpenSans-Regular.ttf'
            )
        )
        # Создание стилей для заголовка и текста.
        header_style = ParagraphStyle(
            'HeaderStyle',
            fontName='OpenSans',
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=25
        )
        regular_style = ParagraphStyle(
            'RegularStyle',
            fontName='OpenSans',
            fontSize=12,
            spaceAfter=10
        )
        # Вёрстка документа.
        header = Paragraph('Список покупок', header_style)
        elements = [header]
        recipes = Recipe.objects.filter(
            shopping_cart_users=request.user
        ).prefetch_related(
            Prefetch(
                'recipe_ingredients',
                queryset=RecipeIngredient.objects.select_related('ingredient')
            )
        )
        for recipe in recipes:
            elements.append(Paragraph(f'{recipe.name}:', regular_style))
            ingredients = [
                f'{recipe_ingredient.ingredient.name} '
                f'({recipe_ingredient.amount} '
                f'{recipe_ingredient.ingredient.measurement_unit})'
                for recipe_ingredient in recipe.recipe_ingredients.all()
            ]
            bullet_points = ListFlowable(
                [
                    ListItem(Paragraph(ingredient, regular_style))
                    for ingredient in ingredients
                ],
                bulletType='bullet'
            )
            elements.append(bullet_points)
        # Генерация и возврат PDF.
        doc.build(elements)
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )
