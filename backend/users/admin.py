from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'email',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscriptions',
        'subscribers',
    )
    search_fields = (
        'username',
        'email',
    )
