from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_by_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_by_is_favorited'
    )
    tags = filters.CharFilter(
        method='filter_by_tags'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_by_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_cart_users__id=self.request.user.id
            )
        return queryset

    def filter_by_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite_users__id=self.request.user.id
            )
        return queryset

    def filter_by_tags(self, queryset, name, value):
        tag_slugs = self.request.query_params.getlist('tags')
        if tag_slugs:
            return queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset
