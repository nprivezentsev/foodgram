from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
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
        # Устанавливается queryset чтобы не возникала ошибка: "Relational field
        # must provide a `queryset` argument, override `get_queryset`, or set
        # read_only=`True`."
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('short_link_code', 'created_at')

    def get_author(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(
            obj.author,
            context=self.context
        ).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
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
        errors = {}
        # Ингредиенты.
        ingredients = self.initial_data.get('ingredients')
        if ingredients is None:
            errors['ingredients'] = 'Обязательное поле.'
        elif not ingredients:
            errors['ingredients'] = (
                'Необходимо указать хотя бы один ингредиент.'
            )
        else:
            ingredient_ids = [ingredient['id'] for ingredient in ingredients]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                errors['ingredients'] = 'Ингредиенты не должны повторяться.'
        # Теги.
        tags = self.initial_data.get('tags')
        if tags is None:
            errors['tags'] = 'Обязательное поле.'
        elif not tags:
            errors['tags'] = 'Необходимо указать хотя бы один тег.'
        elif len(tags) != len(set(tags)):
            errors['tags'] = 'Теги не должны повторяться.'
        # Изображение.
        image = self.initial_data.get('image')
        if not image:
            errors['image'] = 'Значение не должно быть пустым.'
        #
        if errors:
            raise ValidationError(errors)
        return data

    def create(self, validated_data):
        return self.save_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.save_recipe(validated_data, instance)

    def save_recipe(self, validated_data, instance=None):
        """Универсальная функция для создания и обновления."""
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        # Создание или обновление рецепта (пока без ингредиентов и тегов).
        recipe, _ = Recipe.objects.update_or_create(
            id=instance.id if instance else None,
            defaults=validated_data
        )
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
        #
        return recipe

    def to_representation(self, data):
        return (
            RecipeReadSerializer(
                context=self.context
            ).to_representation(data)
        )


class RecipeShortReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseUserRecipeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        abstract = True
        fields = '__all__'

    def validate(self, data):
        if self.Meta.model.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise ValidationError('Рецепт уже добавлен.')
        return data


class ShoppingCartSerializer(BaseUserRecipeSerializer):

    class Meta(BaseUserRecipeSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(BaseUserRecipeSerializer):

    class Meta(BaseUserRecipeSerializer.Meta):
        model = Favorite
