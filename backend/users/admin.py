from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'is_superuser',
        'avatar'
    )
    search_fields = (
        'name',
        'username',
        'first_name',
        'last_name',
        'email'
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar',)
        }),
    )
    ordering = ('username',)
