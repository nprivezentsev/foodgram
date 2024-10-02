from django.core.validators import MinValueValidator

recipe_cooking_time_validator = MinValueValidator(1)
