# Generated by Django 5.2.1 on 2025-05-19 09:12

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_delete_follow'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={
                'default_related_name': 'favorites',
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
            },
        ),
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={
                'verbose_name': 'Ингредиент в рецепте',
                'verbose_name_plural': 'Ингредиенты в рецептах',
            },
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={
                'ordering': ['-pub_date'],
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={
                'default_related_name': 'shopping_carts',
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
        migrations.RemoveConstraint(
            model_name='ingredientrecipe',
            name='unique_ingredients',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_cart',
        ),
        migrations.AlterField(
            model_name='favorite',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор',
            ),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.recipe',
                verbose_name='Рецепт',
            ),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, 'Минимальное количество ингредиентов 1'
                    )
                ],
                verbose_name='Количество',
            ),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.ingredient',
                verbose_name='Ингредиент',
            ),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='ingredient_amounts',
                to='recipes.recipe',
                verbose_name='Рецепт',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(
                help_text='Автор',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipes',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(
                help_text='Добавьте изображение рецепта',
                upload_to='media/',
                verbose_name='Картинка',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                related_name='recipes',
                through='recipes.IngredientRecipe',
                to='recipes.ingredient',
                verbose_name='Ингредиенты',
            ),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор',
            ),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.recipe',
                verbose_name='Рецепт',
            ),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'
            ),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(
                fields=('author', 'recipe'), name='unique_shoppingcart'
            ),
        ),
    ]
