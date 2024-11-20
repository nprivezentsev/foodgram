from textwrap import shorten

from django.db import models

from .constants import (
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    OBJECT_NAME_MAX_DISPLAY_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    RECIPE_SHORT_LINK_CODE_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH
)
from .utils import generate_unique_short_link_code, make_relation_name
from .validators import value_ge_1_validator


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        unique_together = ('name', 'measurement_unit')
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
        'users.User',
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
        verbose_name='Теги',
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='В минутах',
        validators=(value_ge_1_validator,)
    )
    short_link_code = models.CharField(
        verbose_name='Код короткой ссылки',
        max_length=RECIPE_SHORT_LINK_CODE_MAX_LENGTH,
        unique=True,
        default=generate_unique_short_link_code
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-created_at',)
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
        verbose_name_plural = 'Ингредиенты в рецепте'
        unique_together = ('recipe', 'ingredient')
        db_table = 'recipes_recipe_ingredients'

    def __str__(self):
        return make_relation_name(self.recipe, self.ingredient)
