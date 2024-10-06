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
    list_display = (
        'id',
        'name',
        'author',
        'count_favorites'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = [
        RecipeIngredientInline,
    ]
    empty_value_display = settings.EMPTY_FIELD

    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(UserRecipeShoppingCart)
class UserRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
