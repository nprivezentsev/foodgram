from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag

from .filters import IngredientFilter
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .validators import recipe_request_user_validator


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

    def partial_update(self, request, *args, **kwargs):
        recipe_request_user_validator(request.user, self.get_object().author)
        return super().update(request, *args, **kwargs)

    @action(('get',), detail=True, url_path='get-link')
    def get_short_link(self, request, pk):
        return Response({
            'short-link': request.build_absolute_uri(
                f'/s/{self.get_object().id}'
            )
        })
