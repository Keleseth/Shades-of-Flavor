from rest_framework import serializers

from .models import Tag, Ingredient, Recipe, RecipeIngredient
from users.serializers import Base64ImageField, CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )
        read_only_fields = ('name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

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


class RecipeSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients',
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'text',
            'image',
            'cooking_time',
            'tags',
            'ingredients',
            'is_favorited',
            # 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.is_favorited.filter(id=user.id).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
        )
        recipe.tags.set(tags_data)
        recipe_ingredient_list = []
        for ingredient_unit in ingredients_data:
            recipe_ingredient_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_unit['id'],
                    amount=ingredient_unit['amount'],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredient_list)
        return recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
