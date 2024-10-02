from textwrap import shorten

from django.contrib.auth import get_user_model
from django.db import models

from . import constants
from .validators import recipe_cooking_time_validator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=constants.INGREDIENT_NAME_MAX_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=constants.MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'
        ordering = ('name',)
        db_table = 'recipes_ingredient'

    def __str__(self):
        return shorten(
            self.name,
            width=constants.OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=constants.TAG_NAME_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=constants.TAG_SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'
        ordering = ('name',)
        db_table = 'recipes_tag'

    def __str__(self):
        return shorten(
            self.name,
            width=constants.OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
        unique=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images'
    )
    description = models.TextField(
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
        validators=(recipe_cooking_time_validator,)
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
            width=constants.OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        verbose_name='Количество',
        max_digits=constants.DECIMAL_MAX_DIGITS,
        decimal_places=constants.DECIMAL_PLACES
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='uk_recipes_recipe_ingredients'
            ),
        )
        db_table = 'recipes_recipe_ingredients'

    def __str__(self):
        return ''  # Чтобы не отображать избыточную инфу в inline в админке.
