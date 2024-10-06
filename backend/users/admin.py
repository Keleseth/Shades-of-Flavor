from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'firstname',
        'lastname',
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
