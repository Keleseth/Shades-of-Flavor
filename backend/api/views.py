from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework import exceptions, response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .filters import RecipeFilter, IngredientFilter
from .models import Ingredient, Recipe, Tag
from core.permissions import (
    AuthenticatedOrReadOnlyRequest,
    IsAuthorAdminOrReadOnlyObject
)
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingSerializer, TagSerializer)
from .utils import (check_and_add, check_and_delete_from_cart,
                    check_and_delete_from_favorite, get_shopping_list)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients',
        'tags',
        'is_in_shopping_cart',
    ). select_related('author')
    filterset_class = RecipeFilter
    permission_classes = (
        AuthenticatedOrReadOnlyRequest,
        IsAuthorAdminOrReadOnlyObject
    )
    ordering_fields = ('name', 'created_at')
    ordering = ('created_at', 'name',)

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
    """Вью редиректра по короткой ссылке."""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        link = kwargs.get('short_link')
        recipe = get_object_or_404(
            Recipe,
            short_link=link
        )
        recipe_url = reverse('recipes-detail', kwargs={'pk': recipe.id})
        return redirect(recipe_url)
