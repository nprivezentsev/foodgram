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

from .serializers import AuthorSerializer, UserAvatarSerializer
from .validators import validate_recipes_limit, validate_subscription_user

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all().prefetch_related(
        Prefetch('subscription_users', queryset=User.objects.only('id'))
    )

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(('put',), detail=False, url_path='me/avatar')
    def update_avatar(self, request):
        serializer = UserAvatarSerializer(
            request.user,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @update_avatar.mapping.delete
    def delete_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('post',), detail=True, url_path='subscribe')
    def add_subscription(self, request, id):  # noqa: A002
        author = get_object_or_404(User, id=id)
        validate_subscription_user(request.user, author)
        request.user.subscription_authors.add(author)
        recipes_limit = request.query_params.get('recipes_limit')
        validate_recipes_limit(recipes_limit)
        # Создание подзапроса для рецептов автора с ограничением по
        # количеству.
        recipes_queryset = Recipe.objects.all()
        if recipes_limit:
            recipes_queryset = recipes_queryset[:int(recipes_limit)]
        # Prefetch используется, чтобы применить лимит рецептов для автора с
        # минимальным количеством запросов к БД (для производительности).
        author = User.objects.filter(id=author.id).prefetch_related(
            Prefetch(
                'recipes',
                queryset=recipes_queryset,
                to_attr='limited_recipes'
            )
        ).first()
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_subscription.mapping.delete
    def remove_subscription(self, request, id):  # noqa: A002
        author = get_object_or_404(User, id=id)
        if request.user.subscription_authors.filter(id=author.id).exists():
            request.user.subscription_authors.remove(author)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(('get',), detail=False, url_path='subscriptions')
    def get_subscriptions(self, request):
        recipes_limit = request.query_params.get('recipes_limit')
        validate_recipes_limit(recipes_limit)
        # Создание подзапроса для рецептов автора с ограничением по
        # количеству.
        recipes_queryset = Recipe.objects.all()
        if recipes_limit:
            recipes_queryset = recipes_queryset[:int(recipes_limit)]
        # Prefetch используется, чтобы применить лимит рецептов для каждого
        # автора с минимальным количеством запросов к БД (для
        # производительности).
        authors = User.objects.filter(
            subscription_users__id=request.user.id
        ).prefetch_related(
            Prefetch(
                'recipes',
                queryset=recipes_queryset,
                to_attr='limited_recipes'
            )
        )
        paginator = api_settings.DEFAULT_PAGINATION_CLASS()
        authors = paginator.paginate_queryset(authors, request)
        serializer = AuthorSerializer(authors, many=True)
        return paginator.get_paginated_response(serializer.data)
