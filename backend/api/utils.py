from collections import defaultdict

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import response, status

from .models import Recipe, RecipeIngredient


def check_and_add(request, object, serializer_class):
    """
    Фунция выполняет проверки через переданный сериализатор,
    сохраняет объект и возвращает объект сериализатора.
    """
    user = request.user
    serializer = serializer_class(
        data={
            'user': user.id,
            'recipe': object.id
        },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return response.Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


def check_and_delete_from_favorite(request, object):
    """
    Фунция выполняет проверку на существование связующей записи
    модели FavoriteRecipe и удаляет его.
    """
    user = request.user
    if not user.favorited.filter(id=object.id).exists():
        return response.Response(
            {'detail': 'Рецепт отсутствует в избранном.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.favorited.remove(object)
    return response.Response(status=status.HTTP_204_NO_CONTENT)


def check_and_delete_from_cart(request, object):
    """
    Фунция выполняет проверку на существование связующей записи
    модели UserRecipeShoppingCart и удаляет его.
    """
    user = request.user
    if not user.recipes_in_cart.filter(id=object.id).exists():
        return response.Response(
            {'detail': 'Рецепт отсутствует в корзине.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.recipes_in_cart.remove(object)
    return response.Response(status=status.HTTP_204_NO_CONTENT)


def get_shopping_list(request):
    user = request.user

    if not user.is_authenticated:
        return response.Response(
            {'detail': 'Войдите в систему'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    queryset = Recipe.objects.filter(author=user)

    shopping_dict = defaultdict(lambda: [0, ""])
    recipe_ingredients_queryset = RecipeIngredient.objects.filter(
        recipe__in=queryset
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(total_amount=Sum('amount'))

    for item in recipe_ingredients_queryset:
        ingredient_name = item['ingredient__name']
        measurement_unit = item['ingredient__measurement_unit']
        amount = item['total_amount']
        shopping_dict[ingredient_name][0] += amount
        shopping_dict[ingredient_name][1] = measurement_unit

    shopping_list = ""
    for ingredient, (amount, measurement_unit) in shopping_dict.items():
        shopping_list += f'{ingredient} ({measurement_unit}) - {amount}\n'

    shopping_file = HttpResponse(shopping_list, content_type='text/plain')
    shopping_file['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"'
    )
    return shopping_file


def create_recipeingredients(object, ingredients_data):
    recipe_ingredient_list = []
    for ingredient_unit in ingredients_data:
        recipe_ingredient_list.append(
            RecipeIngredient(
                recipe=object,
                ingredient=ingredient_unit['id'],
                amount=ingredient_unit['amount'],
            )
        )
    RecipeIngredient.objects.bulk_create(recipe_ingredient_list)
