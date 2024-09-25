from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientsViewSet, RecipeViewSet
from users.views import UserDjoserViewSet


api_v1 = DefaultRouter()
api_v1.register(r'users', UserDjoserViewSet, basename='users')
api_v1.register(r'tags', TagViewSet, basename='tags')
api_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
api_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
