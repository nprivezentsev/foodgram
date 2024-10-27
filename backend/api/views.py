from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from .filters import IngredientFilter
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .validators import validate_recipe_update_user


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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('post', 'patch', 'get', 'head', 'options')
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def perform_create(self, serializer):
        self.save_recipe(serializer)

    def perform_update(self, serializer):
        self.save_recipe(serializer)

    def partial_update(self, request, *args, **kwargs):
        validate_recipe_update_user(request.user, self.get_object().author)
        return super().partial_update(request, *args, **kwargs)

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
