from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import secrets

from users.models import User


MIN_VALUE_COOKING_TIME = 1
MAX_VALUE_COOKING_TIME = 32_000


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=100,
        db_index=True,
        help_text='Введите название',
    )

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=20,
        help_text='Введите единицу измерения',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        help_text='Автор',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )

    text = models.TextField(
        'Описание',
        help_text='Опишите приготовление рецепта',
    )

    name = models.CharField(
        'Название',
        max_length=150,
        help_text='Введите название рецепта',
        db_index=True,
    )

    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                MIN_VALUE_COOKING_TIME,
                'Минимальное время приготовления 1',
            ),
            MaxValueValidator(
                MAX_VALUE_COOKING_TIME,
                'Максимальное время приготовления 32000',
            ),
        ],
        help_text='Укажите время приготовления рецепта в минутах',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        help_text='Добавьте изображение рецепта',
    )

    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipes'
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
    )

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )

    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE_COOKING_TIME,
                'Минимальное количество ингредиентов 1',
            ),
            MaxValueValidator(
                MAX_VALUE_COOKING_TIME,
                'Максимальное количество ингредиентов 32000',
            ),
        ],
    )

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients'
            )
        ]


class BaseAuthorRecipeRelation(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.author} - {self.recipe}'

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_%(class)s'
            )
        ]


class ShoppingCart(BaseAuthorRecipeRelation):
    class Meta(BaseAuthorRecipeRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'


class Favorite(BaseAuthorRecipeRelation):
    class Meta(BaseAuthorRecipeRelation.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite'


class RecipeShortLink(models.Model):
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link',
    )

    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'Короткая ссылка рецепта'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_urlsafe(6)[:8]
        super().save(*args, **kwargs)
