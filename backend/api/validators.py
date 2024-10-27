from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError


def validate_recipe(initial_data, data):
    errors = {}
    if 'ingredients' not in initial_data:
        errors['ingredients'] = 'Обязательное поле.'
    if 'tags' not in initial_data:
        errors['tags'] = 'Обязательное поле.'
    if errors:
        raise ValidationError(errors)
    return data


def validate_recipe_ingredients(value):
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


def validate_recipe_tags(value):
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


def validate_recipe_image(value):
    if not value:
        raise ValidationError(
            'Значение не должно быть пустым.'
        )
    return value


def validate_recipe_update_user(user, author):
    if user != author:
        raise PermissionDenied(
            'У вас недостаточно прав для выполнения данного действия.'
        )
