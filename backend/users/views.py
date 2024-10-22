from django.conf import settings
from djoser.views import UserViewSet
from rest_framework import pagination, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import (
    AuthenticatedOrReadOnlyRequest,
    IsAuthorAdminOrReadOnlyObject
)
from users.models import CustomUser, Subscription
from users.serializers import (
    CustomUserSerializer,
    GetSubscriptionsSerializer,
    UserAvatarSerializer
)
from users.utils import get_subscription_data


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

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (permissions.AllowAny,)
        return [permission() for permission in self.permission_classes]

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
    def get_subscriptions(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            subscriptions = CustomUser.objects.filter(
                subscriptions__subscribers=request.user
            )
            paginator = pagination.PageNumberPagination()
            paginator.page_size = settings.SUBSCRIPTIONS_PAGE_SIZE
            page = paginator.paginate_queryset(subscriptions, request)
            serializer = GetSubscriptionsSerializer(
                page,
                context={'request': request},
                many=True
            )
            return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(
        methods=[],
        detail=True,
        url_path='subscribe',
    )
    def manage_subscription(self, request, *args, **kwargs):
        """
        Пустая функция для точек входа POST и DELETE HTTP запросов к эндпоинту.
        """
        pass

    @manage_subscription.mapping.post
    def create_subscription(self, request, *args, **kwargs):
        user, subscribed_user = get_subscription_data(request, kwargs)

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

    @manage_subscription.mapping.delete
    def delete_subscription(self, request, *args, **kwargs):
        user, subscribed_user = get_subscription_data(request, kwargs)
        subscription = user.subscribers.filter(
            subscriptions=subscribed_user
        ).first()
        if not subscription:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
