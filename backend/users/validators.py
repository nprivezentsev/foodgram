from django.core.validators import RegexValidator

user_username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=(
        'Имя пользователя должно содержать только буквы, цифры и следующие '
        'символы: @.+-_'
    )
)
