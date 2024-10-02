from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = (
        'name',
        'author__username',
        'author__first_name',
        'author__last_name',
        'author__email'
    )
    list_filter = ('tags',)
    readonly_fields = ('author',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name',)
