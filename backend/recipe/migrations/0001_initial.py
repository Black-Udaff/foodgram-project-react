# Generated by Django 5.0.4 on 2024-05-06 12:57

import colorfield.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=12, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Имя')),
                ('color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, unique=True)),
                ('slug', models.SlugField(max_length=25, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='колличество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipe.ingredient', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Связь ингредиента и рецепта',
                'verbose_name_plural': 'Связи ингредиентов и рецептов',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время больше или равно единице')], verbose_name='Время готовки')),
                ('image', models.ImageField(default=None, null=True, upload_to='recipes/images/')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации рецепта')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('favorites', models.ManyToManyField(blank=True, related_name='favorite_recipes', to=settings.AUTH_USER_MODEL)),
                ('ingredients', models.ManyToManyField(through='recipe.IngredientRecipe', to='recipe.ingredient', verbose_name='Ингредиент')),
                ('shopping_cart', models.ManyToManyField(blank=True, related_name='shoping_recipes', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(to='recipe.tag', verbose_name='тег')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='recipe.recipe', verbose_name='Рецепт'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('subscribed_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
            ],
            options={
                'verbose_name': 'подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredient_recipe'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['subscriber', 'subscribed_to'], name='subscription_idx'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('subscriber', 'subscribed_to'), name='unique_subscription'),
        ),
    ]
