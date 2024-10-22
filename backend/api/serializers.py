from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CustomUserSerializer
from users.utils import Base64ImageField

from .utils import create_recipeingredients
from .base_serializers import BaseRecipeSerializer
from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, Tag,
                     UserRecipeShoppingCart)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = (
            'name',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели между рецептами и ингредиентами."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(BaseRecipeSerializer):
    """Сериализатор рецептов."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        allow_empty=False,
        source='recipe_ingredients',
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
        allow_empty=False,

    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(BaseRecipeSerializer.Meta):
        model = Recipe
        fields = BaseRecipeSerializer.Meta.fields + [
            'author',
            'text',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        ]

    def to_representation(self, instance):
        recipe_representation = super().to_representation(instance)
        tags = instance.tags.all()
        recipe_representation['tags'] = TagSerializer(
            tags,
            many=True
        ).data
        return recipe_representation

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.is_favorited.filter(id=user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj in user.recipes_in_cart.all()
        return False

    def create(self, validated_data):
        user = self.context['request'].user
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        tags_data = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(
            **validated_data,
        )
        recipe.tags.set(tags_data)
        create_recipeingredients(recipe, ingredients_data)
        recipe.is_favorited.add(user)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        tags_data = validated_data.pop('tags', None)
        if tags_data:
            instance.tags.set(tags_data)
        if ingredients_data:
            instance.ingredients.clear()
            create_recipeingredients(instance, ingredients_data)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def validate(self, attrs):
        tags_list = attrs.get('tags')
        if tags_list is None:
            raise serializers.ValidationError(
                'Поле tags обязательное.'
            )
        if len(tags_list) != len(set(tags_list)):
            raise serializers.ValidationError(
                'Нельзя указывать несколько одинаковых тегов.'
            )
        ingredients_list = attrs.get('recipe_ingredients')
        if ingredients_list is None:
            raise serializers.ValidationError(
                'Поле ingredients обязательное.'
            )
        ingredients_id_set = set([object['id'] for object in ingredients_list])
        if len(ingredients_list) != len(ingredients_id_set):
            raise serializers.ValidationError(
                'Нельзя указывать несколько одинаковых ингредиентов.'
            )
        return attrs


class FavoriteOrShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор ответа для: избранных рецептов и корзины покупок."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = FavoriteRecipe
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранных',
            )
        ]

    def to_representation(self, instance):
        recipe = instance.recipe
        return FavoriteOrShoppingSerializer(
            recipe,
        ).data


class ShoppingSerializer(FavoriteSerializer):
    """Сериализатор корзины покупок."""

    class Meta(FavoriteSerializer.Meta):
        model = UserRecipeShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=UserRecipeShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в корзине',
            )
        ]
