from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers import RecipeShortReadSerializer
from foodgram.constants import PARAM_RECIPES_LIMIT_MIN_VALUE

from .models import Subscription

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscription_users.filter(user=user).exists()
        )


class UserSerializer(BaseUserSerializer, DjoserUserSerializer):

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class AuthorSerializer(BaseUserSerializer):
    recipes = RecipeShortReadSerializer(many=True, source='limited_recipes')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого автора.')
        return data


class RecipesLimitSerializer(serializers.Serializer):
    recipes_limit = serializers.IntegerField(
        required=False, min_value=PARAM_RECIPES_LIMIT_MIN_VALUE
    )
