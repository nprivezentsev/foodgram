from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return False


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class UserAvatarAddSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
