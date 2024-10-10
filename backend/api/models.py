import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

CustomUser = get_user_model()


class Tag(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='тег'
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name='слаг'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=128,
        verbose_name='ингредиент',
        unique=True,

    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='ед. измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """МОдель рецептов."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='название рецепта'
    )
    is_favorited = models.ManyToManyField(
        CustomUser,
        through='FavoriteRecipe',
        related_name='favorited',
        verbose_name='избранные рецепты'
    )
    text = models.TextField(
        verbose_name='описание рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.POSITIVE_SMALL_INTEGER_MIN),
            MaxValueValidator(settings.POSITIVE_SMALL_INTEGER_MAX),
        ],
        verbose_name='время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )
    is_in_shopping_cart = models.ManyToManyField(
        CustomUser,
        through='UserRecipeShoppingCart',
        related_name='recipes_in_cart',
        verbose_name='список покупок'
    )
    short_link = models.CharField(
        max_length=9,
        unique=True,
        blank=True,
        null=True,
        verbose_name='короткая ссылка',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = uuid.uuid4().hex[:9]
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    """Связующая таблица между рецептами и ингредиентами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(settings.POSITIVE_SMALL_INTEGER_MIN),
            MaxValueValidator(settings.POSITIVE_SMALL_INTEGER_MAX),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_for_recipe',
            )
        ]
        verbose_name = 'ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self) -> str:
        return f'{self.ingredient.name} для рецепта: {self.recipe.name}'


class FavoriteRecipe(models.Model):
    """Модель для любимых рецептов пользователей."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe',
            )
        ]
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return (
            f'Любимый рецепт пользователя {self.user.username}: '
            f'{self.recipe.name}'
        )


class UserRecipeShoppingCart(models.Model):
    """Модель корзины покупок для пользователей."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_cart',
            )
        ]
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'

    def __str__(self) -> str:
        return (
            f'Рецепт: {self.recipe.name} в корзине пользователя '
            f'{self.user.username}: '
        )
