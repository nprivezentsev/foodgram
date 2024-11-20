from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from .validators import (
    validate_recipe,
    validate_recipe_image,
    validate_recipe_ingredients,
    validate_recipe_tags
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(  # noqa: A003
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount,
        }


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        exclude = (
            'short_link_code',
            'created_at'
        )

    def validate(self, data):
        return validate_recipe(self.initial_data, data)

    def validate_ingredients(self, value):
        return validate_recipe_ingredients(value)

    def validate_tags(self, value):
        return validate_recipe_tags(value)

    def validate_image(self, value):
        return validate_recipe_image(value)

    def to_representation(self, instance):
        from users.serializers import UserSerializer
        user = self.context['request'].user
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        representation['author'] = UserSerializer(
            instance.author,
            context={'request': self.context['request']}
        ).data
        if user.is_authenticated:
            representation['is_favorited'] = (
                user in instance.favorite_users.all()
            )
            representation['is_in_shopping_cart'] = (
                user in instance.shopping_cart_users.all()
            )
        else:
            representation['is_favorited'] = False
            representation['is_in_shopping_cart'] = False
        return representation


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
