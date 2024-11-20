from textwrap import shorten

from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe
from recipes.utils import make_relation_name

from .constants import (
    OBJECT_NAME_MAX_DISPLAY_LENGTH,
    USER_EMAIL_MAX_LENGTH,
    USER_NAME_MAX_LENGTH
)
from .validators import user_username_validator


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=USER_NAME_MAX_LENGTH,
        unique=True,
        validators=(user_username_validator,)
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=USER_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=USER_NAME_MAX_LENGTH
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/avatars/',
        blank=True
    )
    subscription_authors = models.ManyToManyField(
        'self',
        verbose_name='Подписан на авторов',
        related_name='subscription_users',
        symmetrical=False,
        blank=True,
        through='Subscription'
    )
    favorite_recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Избранные рецепты',
        related_name='favorite_users',
        blank=True,
        through='Favorite'
    )
    shopping_cart_recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты в корзине',
        related_name='shopping_cart_users',
        blank=True,
        through='ShoppingCart'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        db_table = 'users_user'

    def __str__(self):
        return shorten(
            self.username,
            width=OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='chk_users_subscription_prevent_self_subscription'
            )
        ]
        db_table = 'users_subscriptions'

    def __str__(self):
        return make_relation_name(self.user, self.author)


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        unique_together = ('user', 'recipe')
        db_table = 'users_favorites'

    def __str__(self):
        return make_relation_name(self.user, self.recipe)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        unique_together = ('user', 'recipe')
        db_table = 'users_shopping_carts'

    def __str__(self):
        return make_relation_name(self.user, self.recipe)
