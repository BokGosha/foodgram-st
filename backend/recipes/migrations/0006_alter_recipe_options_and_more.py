# Generated by Django 5.2.1 on 2025-05-20 14:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_favorite_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={
                'default_related_name': 'recipes',
                'ordering': ['-pub_date'],
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.RemoveConstraint(
            model_name='ingredientrecipe',
            name='unique_recipe_ingredient',
        ),
        migrations.RemoveConstraint(
            model_name='recipe',
            name='unique_recipe',
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredients',
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
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                through='recipes.IngredientRecipe',
                to='recipes.ingredient',
                verbose_name='Ингредиенты',
            ),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_ingredients'
            ),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(
                fields=('name', 'author'), name='unique_recipes'
            ),
        ),
    ]
