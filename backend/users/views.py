from djoser.views import UserViewSet
from users.models import CustomUser, Subscription
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, pagination
from .serializers import UserDjoserSerializer
from rest_framework.decorators import action
from .serializers import UserDjoserSerializer, CustomUserSerializer, GetSubscriptionsSerializer


class UserDjoserViewSet(UserViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination

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
        url_name='user_subscriptions'
    )
    def get_subscriptiosn(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            subscriptions = CustomUser.objects.filter(
                subscriptions__subscribers=request.user
            )
            paginator = pagination.PageNumberPagination()
            paginator.page_size = 10
            page = paginator.paginate_queryset(subscriptions, request)
            serializer = GetSubscriptionsSerializer(
                page,
                context={'request': request},
                many=True
            )
            return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
    )
    def add_delete_subscription(self, request, *args, **kwargs):
        user = request.user
        subscribed_user_id = kwargs.get('id')
        try:
            subscribed_user = CustomUser.objects.get(id=subscribed_user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if request.method == 'POST':
            if user.subscriptions.filter(subscribers=subscribed_user).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на данного пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                subscriptions=subscribed_user,
                subscribers=user
            )
            serializer = GetSubscriptionsSerializer(
                subscribed_user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)