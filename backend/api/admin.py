from django.contrib import admin
from django.conf import settings

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    UserRecipeShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке рецептов в админке
    list_display = (
        'id',  # Идентификатор рецепта
        'name',  # Название рецепта
        'author',  # Автор рецепта
        'count_favorites'  # Количество пользователей, добавивших рецепт в избранное
    )
    # Поля, по которым можно искать рецепты
    search_fields = ('name', 'author__username')  # Поиск по названию рецепта и имени автора
    # Фильтры в админке для удобства поиска рецептов по тегам
    list_filter = ('tags',)  # Фильтр по тегам рецептов
    # Встроенные записи для редактирования ингредиентов рецепта на странице рецепта
    inlines = [
        RecipeIngredientInline,  # Позволяет редактировать ингредиенты прямо в рецепте
    ]
    # Отображение значения, если поле пустое
    empty_value_display = settings.EMPTY_FIELD  # Заменяет пустые значения в админке на значение, указанное в настройках

    # Метод для подсчета количества пользователей, добавивших рецепт в избранное
    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(UserRecipeShoppingCart)
class UserRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
