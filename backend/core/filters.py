from django_filters import rest_framework as filters

from api.models import Recipe
from users.models import CustomUser


class RecipeFilter(filters.FilterSet):
    """Кастомный класс фильтрации запросов."""

    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value is True and user.is_authenticated:
            return queryset.filter(is_favorited=user)
        if value is False and user.is_authenticated:
            return queryset.exclude(is_favorited=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value is True and user.is_authenticated:
            return queryset.filter(is_in_shopping_cart=user)
        return queryset
