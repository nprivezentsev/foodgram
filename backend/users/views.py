from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings

from recipes.models import Recipe

from .models import Subscription
from .serializers import (
    AuthorSerializer,
    RecipesLimitSerializer,
    SubscriptionSerializer,
    UserAvatarSerializer
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(('put',), detail=False, url_path='me/avatar')
    def update_avatar(self, request):
        serializer = UserAvatarSerializer(
            request.user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @update_avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('post',), detail=True, url_path='subscribe')
    def add_subscription(self, request, id):  # noqa: A002
        recipes_limit_serializer = RecipesLimitSerializer(
            data=request.query_params, context={'request': request}
        )
        recipes_limit_serializer.is_valid(raise_exception=True)
        recipes_limit = recipes_limit_serializer.validated_data.get(
            'recipes_limit'
        )
        # Создание подзапроса для рецептов автора с ограничением по
        # количеству.
        recipes_queryset = Recipe.objects.all()
        if recipes_limit:
            recipes_queryset = recipes_queryset[:recipes_limit]
        # Prefetch используется, чтобы применить лимит рецептов для автора с
        # минимальным количеством запросов к БД (для производительности).
        author = get_object_or_404(
            User.objects.filter(id=id).prefetch_related(
                Prefetch(
                    'recipes',
                    queryset=recipes_queryset,
                    to_attr='limited_recipes'
                )
            )
        )
        subscription_serializer = SubscriptionSerializer(
            data={'author': author.id}, context={'request': request}
        )
        subscription_serializer.is_valid(raise_exception=True)
        subscription_serializer.save()
        return Response(
            AuthorSerializer(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @add_subscription.mapping.delete
    def remove_subscription(self, request, id):  # noqa: A002
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(('get',), detail=False, url_path='subscriptions')
    def get_subscriptions(self, request):
        limit_serializer = RecipesLimitSerializer(
            data=request.query_params
        )
        limit_serializer.is_valid(raise_exception=True)
        recipes_limit = limit_serializer.validated_data.get(
            'recipes_limit'
        )
        # Создание подзапроса для рецептов автора с ограничением по
        # количеству.
        recipes_queryset = Recipe.objects.all()
        if recipes_limit:
            recipes_queryset = recipes_queryset[:recipes_limit]
        # Prefetch используется, чтобы применить лимит рецептов для каждого
        # автора с минимальным количеством запросов к БД (для
        # производительности).
        authors = User.objects.filter(
            subscription_users__user=request.user
        ).prefetch_related(
            Prefetch(
                'recipes',
                queryset=recipes_queryset,
                to_attr='limited_recipes'
            )
        )
        paginator = api_settings.DEFAULT_PAGINATION_CLASS()
        authors = paginator.paginate_queryset(authors, request)
        return paginator.get_paginated_response(
            AuthorSerializer(
                authors, many=True, context={'request': request}
            ).data
        )
