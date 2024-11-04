from textwrap import shorten

from django.contrib.auth.models import AbstractUser
from django.db import models

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
        null=True,
        blank=True
    )
    subscription_authors = models.ManyToManyField(
        'self',
        verbose_name='Подписан на авторов',
        related_name='subscription_users',
        symmetrical=False,
        blank=True
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
