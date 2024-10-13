from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet

api_v1 = DefaultRouter()
api_v1.register(r'users', CustomUserViewSet, basename='users')
api_v1.register(r'tags', TagViewSet, basename='tags')
api_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
api_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
