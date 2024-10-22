from django_filters import rest_framework as filters

from api.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class IngredientFilter(filters.FilterSet):
    """Кастомная Фильтрация тегов"""

    name = filters.CharFilter(
        lookup_expr='istartswith',
        help_text=(
            'Регистронезависимая фильтрация ингредиентов по названию '
            'начиная с указанных в запросе символов'
        )
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Кастомная фильтрации рецептов."""

    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
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
        if value is False and user.is_authenticated:
            return queryset.exclude(is_favorited=user)
        return queryset
