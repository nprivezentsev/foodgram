from textwrap import shorten

from django.contrib.auth import get_user_model
from django.db import models

from .constants import (
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    OBJECT_NAME_MAX_DISPLAY_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH
)
from .validators import value_ge_1_validator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        db_table = 'recipes_ingredient'

    def __str__(self):
        return shorten(
            self.name,
            width=OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_NAME_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        db_table = 'recipes_tag'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
        unique=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='В минутах',
        validators=(value_ge_1_validator,)
    )
    shopping_cart_users = models.ManyToManyField(
        User,
        related_name='shopping_cart_recipes',
        verbose_name='В корзине у пользователей'
    )
    favorite_users = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        verbose_name='В избранном у пользователей'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('name',)
        db_table = 'recipes_recipe'

    def __str__(self):
        return shorten(
            self.name,
            width=OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=(value_ge_1_validator,)
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('recipe', 'ingredient')
        db_table = 'recipes_recipe_ingredients'

    def __str__(self):
        return (
            shorten(
                self.recipe,
                width=OBJECT_NAME_MAX_DISPLAY_LENGTH // 2,
                placeholder=' ...'
            )
            + ' - '
            + shorten(
                self.ingredient,
                width=OBJECT_NAME_MAX_DISPLAY_LENGTH // 2,
                placeholder=' ...'
            )
        )
