import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

CustomUser = get_user_model()


# class IngredientManagerCSV(models.BaseManager):
#     def load_csv_data(self, csv_file_path):
#         with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             ingredients = []
#             for row in reader:
#                 if len(row) == 2:
#                     name = row[0].strip()
#                     unit = row[1].strip()
#                     ingredient = self.model(name=name, unit=unit)
#                     ingredients.append(ingredient)
#             self.bulk_create(ingredients)


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

    # csv_manager = IngredientManagerCSV


class Ingredient(models.Model):
    """Модель ингредиентов."""

    # MEASURE_UNITS = [ TODO
    # ]

    name = models.CharField(
        max_length=128,
        verbose_name='ингредиент',
        unique=True,

    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='ед. измерения'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


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
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999),
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
        'Дата публикации',
        auto_now_add=True,
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

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = uuid.uuid4().hex[:9]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)


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
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')


class FavoriteRecipe(models.Model):
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


class UserRecipeShoppingCart(models.Model):
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
