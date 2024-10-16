from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError


def recipe_ingredients_validator(value):
    if not value:
        raise ValidationError(
            'Необходимо указать хотя бы один ингредиент.'
        )
    ingredient_ids = [ingredient['ingredient'].id for ingredient in value]
    if len(ingredient_ids) != len(set(ingredient_ids)):
        raise ValidationError(
            'Ингредиенты не должны повторяться.'
        )
    return value


def recipe_tags_validator(value):
    if not value:
        raise ValidationError(
            'Необходимо указать хотя бы один тег.'
        )
    tag_ids = [tag.id for tag in value]
    if len(tag_ids) != len(set(tag_ids)):
        raise ValidationError(
            'Теги не должны повторяться.'
        )
    return value


def recipe_image_validator(value):
    if not value:
        raise ValidationError(
            'Значение не должно быть пустым.'
        )
    return value


def recipe_request_user_validator(request_user, recipe_author):
    if request_user != recipe_author:
        raise PermissionDenied(
            'У вас недостаточно прав для выполнения данного действия.'
        )
