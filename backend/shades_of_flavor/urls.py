from django.contrib import admin
from django.urls import path, include

from api.views import RecipeRedirectApiView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_link>/', RecipeRedirectApiView.as_view(), name='short-link'),
]
