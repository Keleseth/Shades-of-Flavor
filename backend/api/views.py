from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters import rest_framework as filters
from rest_framework import exceptions, response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser

from .models import Ingredient, Recipe, Tag
from .permissions import AuthenticatedOrReadOnlyRequest, AuthorAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingSerializer, TagSerializer)
from .utils import (check_and_add, check_and_delete_from_cart,
                    check_and_delete_from_favorite, get_shopping_list)


class RecipeFilter(filters.FilterSet):

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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients',
        'tags',
    ). select_related('author')
    filterset_class = RecipeFilter
    permission_classes = (AuthorAdminOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        url_path='favorite',
        url_name='favorite',
        permission_classes=(AuthenticatedOrReadOnlyRequest,),
    )
    def add_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            return check_and_add(
                request, recipe, FavoriteSerializer
            )

        if request.method == 'DELETE':
            return check_and_delete_from_favorite(
                request, recipe
            )
        return response.Response(
            {'detail': 'Метод запроса запрещен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        ['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def add_to_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            return check_and_add(
                request, recipe, ShoppingSerializer
            )

        if request.method == 'DELETE':
            return check_and_delete_from_cart(request, recipe)
        return response.Response(
            {'detail': 'Метод запроса запрещен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        ['GET'],
        detail=True,
        url_path='get-link',
    )
    def recipe_short_link(self, request, pk):
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            raise exceptions.NotFound('Рецепт не найден.')

        domain = f'{request.scheme}://{request.get_host()}'

        short_link_url = recipe.short_link
        return response.Response(
            {'short-link': f'{domain}/s/{short_link_url}'},
            status=status.HTTP_200_OK
        )

    @action(
        ['GET'],
        detail=False,
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        return get_shopping_list(request)


class RecipeRedirectApiView(views.APIView):
    def get(self, request, *args, **kwargs):
        link = kwargs.get('short_link')
        recipe = get_object_or_404(
            Recipe,
            short_link=link
        )
        recipe_url = reverse('recipes-detail', kwargs={'pk': recipe.id})
        return redirect(recipe_url)
