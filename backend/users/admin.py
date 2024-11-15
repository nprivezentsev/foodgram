from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['user'] == cleaned_data['author']:
            self.add_error('author', 'Нельзя подписаться на самого себя.')


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    form = SubscriptionForm
    fk_name = 'user'
    extra = 0
    verbose_name = 'объект "Подписка"'
    verbose_name_plural = 'Подписки'


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
    inlines = (SubscriptionInline,)
    ordering = ('username',)
