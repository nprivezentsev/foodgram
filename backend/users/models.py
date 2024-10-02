from textwrap import shorten

from django.contrib.auth.models import AbstractUser
from django.db import models

from . import constants, validators


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=constants.USER_EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=constants.USER_NAME_MAX_LENGTH,
        unique=True,
        validators=(validators.user_username_validator,)
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=constants.USER_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=constants.USER_NAME_MAX_LENGTH
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/avatars/',
        null=True,
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
            width=constants.OBJECT_NAME_MAX_DISPLAY_LENGTH,
            placeholder=' ...'
        )
