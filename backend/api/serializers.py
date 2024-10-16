from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer

from .validators import (
    recipe_image_validator,
    recipe_ingredients_validator,
    recipe_tags_validator
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
        fields = '__all__'

    def validate_ingredients(self, value):
        return recipe_ingredients_validator(value)

    def validate_tags(self, value):
        return recipe_tags_validator(value)

    def validate_image(self, value):
        return recipe_image_validator(value)

    def create(self, validated_data):
        recipe = Recipe()
        return self.save_recipe(recipe, validated_data)

    def update(self, instance, validated_data):
        return self.save_recipe(instance, validated_data)

    def save_recipe(self, recipe, validated_data):
        """Универсальная функция для create и update."""
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        # Обновляем или создаём рецепт (пока без ингредиентов и тегов).
        recipe, created = Recipe.objects.update_or_create(
            pk=recipe.pk,
            defaults=validated_data
        )
        # Обновляем или создаём ингредиенты.
        if recipe.recipe_ingredients.exists():
            recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
        # Обновляем или создаём теги.
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        representation['author'] = UserSerializer(instance.author).data
        representation['is_favorited'] = False
        representation['is_in_shopping_cart'] = False
        return representation
