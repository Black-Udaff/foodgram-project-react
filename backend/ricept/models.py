from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=128)
    measurement_unit = models.CharField("Единица измерения", max_length=12)

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("Имя", max_length=128, unique=True)
    color = models.CharField(max_length=16, unique=True)
    slug = models.SlugField("Слаг", max_length=25, unique=True)

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField("Название", max_length=128)
    text = models.TextField("Описание")
    cooking_time = models.PositiveIntegerField(
        "Время готовки",
        validators=[
            MinValueValidator(1, message="ололо"),
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )

    image = models.ImageField(upload_to="recipes/images/",
                              null=True,
                              default=None)
    ingredients = models.ManyToManyField(
        Ingredient, through="Ingredient_Recipe", verbose_name="Ингредиент"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Ингредиент")
    favorites = models.ManyToManyField(
        User, related_name="favorite_recipes", blank=True
    )
    shopping_cart = models.ManyToManyField(
        User, related_name="shoping_recipes", blank=True
    )

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Ingredient_Recipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        "колличество",
    )

    class Meta:
        verbose_name = "Связь жанра и произведения"
        verbose_name_plural = "Связи жанров и произведений"


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        related_name="following",  # Пользователь, который подписывается
        on_delete=models.CASCADE,
    )
    subscribed_to = models.ForeignKey(
        User,
        related_name="followers",  # Пользователь, на которого подписываются
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )  # Дата и время создания подписки

    class Meta:
        unique_together = (
            "subscriber",
            "subscribed_to",
        )  # Гарантируем уникальность подписок
        indexes = [
            models.Index(
                fields=["subscriber", "subscribed_to"], name="subscription_idx"
            )
        ]

    def __str__(self):
        return (
            f"{self.subscriber.username} is subscribed"
            f"to {self.subscribed_to.username}"
        )
