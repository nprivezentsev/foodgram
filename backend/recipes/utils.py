import secrets

from .constants import RECIPE_SHORT_LINK_CODE_MAX_LENGTH


def generate_unique_short_link_code():
    from .models import Recipe
    while True:
        random_code = (
            secrets.token_urlsafe().replace('_', '').replace('-', '')[
                :RECIPE_SHORT_LINK_CODE_MAX_LENGTH
            ].lower()
        )
        if not Recipe.objects.filter(short_link_code=random_code).exists():
            return random_code
