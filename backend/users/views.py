from djoser.views import UserViewSet
from rest_framework import pagination, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import (
    AuthenticatedOrReadOnlyRequest,
    IsAuthorAdminOrReadOnlyObject
)
from users.models import CustomUser, Subscription

from .serializers import (
    CustomUserSerializer,
    GetSubscriptionsSerializer,
    UserAvatarSerializer
)
from .validators import subscription_creatable


class CustomUserViewSet(UserViewSet):
    """Вьюсет пользователей."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (
        AuthenticatedOrReadOnlyRequest,
        IsAuthorAdminOrReadOnlyObject
    )
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size_query_param = 'limit'

    def list(self, request, *args, **kwargs):
        queryset = CustomUser.objects.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        ['PUT', 'DELETE'],
        detail=False,
        url_path='me/avatar',
        permission_classes=(AuthenticatedOrReadOnlyRequest,)
    )
    def change_avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserAvatarSerializer(data=request.data, partial=True)
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
        subscribed_user_id = kwargs['id']
        subscribed_user = subscription_creatable(user, subscribed_user_id)
        if request.method == 'POST':
            if user.subscribers.filter(subscriptions=subscribed_user).exists():
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

        if request.method == 'DELETE':
            if not user.subscribers.filter(
                subscriptions=subscribed_user
            ).exists():
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.get(
                subscriptions=subscribed_user,
                subscribers=user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Метод запроса запрещен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
