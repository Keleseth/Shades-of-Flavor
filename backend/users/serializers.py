from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.base_serializers import BaseRecipeSerializer
from users.models import CustomUser
from users.utils import Base64ImageField


class BaseCustomUserSerializer(UserSerializer):
    """Базовый сериализатор юзеров."""

    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.subscriptions.filter(
                subscribers=request.user
            ).exists()
        return False


class CustomUserSerializer(BaseCustomUserSerializer):
    """Сериализатор юзеров для регистрации с полем password."""

    class Meta(BaseCustomUserSerializer.Meta):
        fields = BaseCustomUserSerializer.Meta.fields + ['password']

        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для обработки аватаров пользователей."""

    avatar = Base64ImageField(required=False, allow_null=True)
    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'avatar',
        )

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {'detail': 'Файл аватарки не был передан.'}
            )
        return attrs


class GetSubscriptionsSerializer(BaseCustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = BaseRecipeSerializer(
        read_only=True,
        many=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta(BaseCustomUserSerializer.Meta):
        fields = BaseCustomUserSerializer.Meta.fields + [
            'recipes',
            'recipes_count',
        ]

    def get_recipes_count(self, obj):
        recipes = obj.recipes.all()
        return recipes.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context['request']
        limit = request.query_params.get('recipes_limit')

        if limit:
            representation['recipes'] = representation['recipes'][:int(limit)]
        return representation
