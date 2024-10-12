from django_filters import rest_framework as filters

from api.models import Recipe, Ingredient
from users.models import CustomUser

# Фильтры в Django REST Framework используются для автоматической фильтрации объектов модели на основе параметров, переданных в запросе.
# Они позволяют пользователям ограничивать результаты по определённым критериям (например, фильтровать рецепты по автору или тегам).
# Фильтры вступают в действие, когда сервер получает запрос с параметрами, соответствующими полям фильтров.
# Например, при запросе с параметром '?tags=breakfast' будет возвращён список рецептов, содержащих тег 'breakfast'.
# Таким образом, фильтры упрощают работу с API, позволяя пользователям получать только нужные данные без необходимости писать сложные запросы вручную.
# АТРИБУТ fields указывает на то, какой параметр фильтрации ожидается из запроса ?name=...  , это означает, что если в fields = ('name',) есть поле name, то фильтрация
# будет фильтровать возвращаемый кверисет по полю name в модели согласно заданому параметру в запросе.
# Параметры is_favorited и is_in_shopping_cart не указаны в атрибуте fields, так как они используют кастомные методы фильтрации (filter_is_favorited и filter_is_in_shopping_cart),
# и их логика отличается от простой фильтрации по полям модели. Эти фильтры обрабатываются отдельно, чтобы учесть дополнительные условия, такие как текущий пользователь.

class IngredientFilter(filters.FilterSet):
    """Кастомная фильтрация ингредиентов."""

    name = filters.CharFilter(
        lookup_expr='istartswith',  # Фильтрация по названию ингредиента, начиная с введённых символов, без учёта регистра
        help_text=(
            'Регистронезависимая фильтрация ингредиентов по названию '
            'начиная с указанных в запросе символов'
        )
    )

    class Meta:
        model = Ingredient
        fields = ('name',)  # Фильтрация возможна только по полю 'name'


class RecipeFilter(filters.FilterSet):
    """Кастомная фильтрация рецептов."""

    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())  # Фильтрация по автору рецепта
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')  # Фильтрация по тегам рецепта (slug тегов)
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',  # Пользовательская фильтрация по избранным рецептам
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'  # Пользовательская фильтрация по наличию рецептов в корзине
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
        )

    def filter_is_favorited(self, queryset, name, value):
        # Фильтрует рецепты по пользователю, добавившему их в избранное
        user = self.request.user
        if value is True and user.is_authenticated:
            return queryset.filter(is_favorited=user)
        if value is False and user.is_authenticated:
            return queryset.exclude(is_favorited=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        # Фильтрует рецепты по наличию в корзине пользователя
        user = self.request.user
        if value is True and user.is_authenticated:
            return queryset.filter(is_in_shopping_cart=user)
        return queryset