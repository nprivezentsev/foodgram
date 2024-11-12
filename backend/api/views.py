from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib import enums, pagesizes, styles
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
    queryset = Recipe.objects.prefetch_related(
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
        # Создание или обновление рецепта (пока без ингредиентов и тегов).
        recipe = serializer.save()
        # Создание или обновление ингредиентов.
        recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
        # Создание или обновление тегов.
        recipe.tags.set(tags)
        return recipe

    @action(('get',), detail=True, url_path='get-link')
    def get_short_link(self, request, pk):
        return Response({
            'short-link': request.build_absolute_uri(
                f'/s/{self.get_object().short_link_code}'
            )
        })

    @action(('post',), detail=True, url_path='shopping_cart')
    def add_to_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.user in recipe.shopping_cart_users.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.shopping_cart_users.add(request.user)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.user not in recipe.shopping_cart_users.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.shopping_cart_users.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('post',), detail=True, url_path='favorite')
    def add_to_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.user in recipe.favorite_users.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.favorite_users.add(request.user)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.user not in recipe.favorite_users.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.favorite_users.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=pagesizes.letter)
        # Регистрация шрифта.
        pdfmetrics.registerFont(
            TTFont(
                'OpenSans',
                settings.BASE_DIR / 'fonts/OpenSans-Regular.ttf'
            )
        )
        # Создание стилей для заголовка и текста.
        header_style = styles.ParagraphStyle(
            'HeaderStyle',
            fontName='OpenSans',
            fontSize=14,
            alignment=enums.TA_CENTER,
            spaceAfter=25
        )
        regular_style = styles.ParagraphStyle(
            'RegularStyle',
            fontName='OpenSans',
            fontSize=12,
            spaceAfter=10
        )
        # Запрос списка покупок пользователя.
        recipes = Recipe.objects.filter(
            shopping_cart_users__id=request.user.id
        ).prefetch_related(
            Prefetch(
                'recipe_ingredients',
                queryset=RecipeIngredient.objects.select_related('ingredient')
            )
        )
        # Суммирование количества каждого ингредиента.
        ingredients_summary = {}
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient_name = recipe_ingredient.ingredient.name
                measurement_unit = (
                    recipe_ingredient.ingredient.measurement_unit
                )
                if ingredient_name in ingredients_summary:
                    ingredients_summary[ingredient_name]['total_amount'] += (
                        recipe_ingredient.amount
                    )
                else:
                    ingredients_summary[ingredient_name] = {
                        'total_amount': recipe_ingredient.amount,
                        'measurement_unit': measurement_unit
                    }
        # Формиравание заголовка и списка ингредиентов с буллетами.
        header = Paragraph('Список покупок', header_style)
        bullet_points = ListFlowable(
            [
                ListItem(
                    Paragraph(
                        f'{ingredient_name} — {data["total_amount"]} '
                        f'{data["measurement_unit"]}',
                        regular_style
                    )
                )
                for ingredient_name, data in ingredients_summary.items()
            ],
            bulletType='bullet'
        )
        # Генерация и возврат PDF.
        doc.build([header, bullet_points])
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )


def redirect_to_recipe(request, code):
    recipe = get_object_or_404(Recipe, short_link_code=code)
    return redirect(
        reverse(
            'api:recipes-detail',
            kwargs={'pk': recipe.id}
        ).replace('/api', '')
    )
