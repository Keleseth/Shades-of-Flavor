from rest_framework import serializers

from .models import Recipe


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для представления рецепта."""

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]
