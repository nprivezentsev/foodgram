from django.core.validators import RegexValidator
from rest_framework.serializers import ValidationError

user_username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=(
        'Имя пользователя должно содержать только буквы, цифры и следующие '
        'символы: @.+-_'
    )
)


def validate_subscription_user(user, author):
    if user == author:
        raise ValidationError(
            {'detail': 'Нельзя подписаться на самого себя.'}
        )
    if author in user.subscription_authors.all():
        raise ValidationError(
            {'detail': 'Вы уже подписаны на этого автора.'}
        )


def validate_recipes_limit(value):
    if value is None:
        return None
    try:
        limit = int(value)
        if limit < 1:
            raise ValidationError(
                {'detail': 'Параметр recipes_limit должен быть больше 0.'}
            )
        return limit
    except ValueError:
        raise ValidationError(
            {'detail': 'Параметр recipes_limit должен быть целым числом.'}
        )
