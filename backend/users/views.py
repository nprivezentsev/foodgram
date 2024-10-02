from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserAvatarAddSerializer


class UserViewSet(DjoserUserViewSet):

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(('put',), detail=False, url_path='me/avatar')
    def add_avatar(self, request):
        serializer = UserAvatarAddSerializer(
            request.user,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @add_avatar.mapping.delete
    def delete_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
