from api.views import RecipeRedirectApiView
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        's/<str:short_link>/',
        RecipeRedirectApiView.as_view(),
        name='short-link',
    )
]
