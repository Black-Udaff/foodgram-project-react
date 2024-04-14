from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=12)

class Tag(models.Model):
    name = models.CharField('Имя', max_length=128, unique=True)
    color = models.CharField(max_length=16, unique=True)
    slug = models.SlugField('Слаг', max_length=25, unique=True)

class Recipe(models.Model):
    name = models.CharField('Название', max_length=128)
    description = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время готовки',
        validators=[
            MinValueValidator(1, message='ололо'),
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='Ingredient_Recipe', verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,  verbose_name='Ингредиент'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
    

class Ingredient_Recipe(models.Model):
    recipe_id = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    ingredient_id = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField('колличество',)

    class Meta:
        verbose_name = 'Связь жанра и произведения'
        verbose_name_plural = 'Связи жанров и произведений'