from djoser.views import UserViewSet
from users.models import CustomUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserDjoserSerializer
from rest_framework.decorators import action
from .serializers import UserDjoserSerializer, CustomUserSerializer


class UserDjoserViewSet(UserViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @action(
        ['PUT', 'DELETE'],
        detail=False,
        url_path='me/avatar',
    )
    def change_avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserDjoserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        avatar_data = serializer.validated_data.get('avatar')
        user.avatar = avatar_data
        user.save()
        image_url = request.build_absolute_uri(
            request.user.avatar.url
        )
        return Response({'avatar': str(image_url)}, status=status.HTTP_200_OK)

    @action(
        ['GET'],
        detail=False,
        url_path='subscriptions',
    )
    def get_subscriptiosn(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            # serializer = 
