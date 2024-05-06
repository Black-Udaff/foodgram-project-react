from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .models import Ingredient, IngredientRecipe, Recipe, Tag
from .fields import Base64ImageField
from .mixins import IsSubscribedMixin
User = get_user_model()


class SimplifiedRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        read_only=True,
    )
    amount = serializers.IntegerField(required=False)
    id = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    id = serializers.IntegerField(source="ingredient.id", read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class UserSerializer(UserSerializer, IsSubscribedMixin):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    ingredients = IngredientSerializer(many=True, required=True)
    image = Base64ImageField(required=True)
    author = SlugRelatedField(
        read_only=True,
        slug_field="username",
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ["favorites", "shopping_cart", "pub_date"]

    def validate(self, data):
        request = self.context.get("request")
        if request and request.method == 'PATCH':
            if "tags" not in data:
                raise serializers.ValidationError(
                    {"tags": "Это поле обязательно для обновления."})
            if "ingredients" not in data:
                raise serializers.ValidationError(
                    {"ingredients": "Это поле обязательно для обновления."})
        return super().validate(data)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент."
            )

        for ingredient_data in ingredients:
            ingredient_id = ingredient_data.get("id")
            try:
                Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {"ingredient": f"Ингр с ID {ingredient_id} не существует."}
                )

            amount = ingredient_data.get("amount", 0)
            if amount < 1:
                raise serializers.ValidationError(
                    {"amount": "Количество ингредиента должно быть больше 0!"}
                )

        ingredient_ids = [data["id"] for data in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredient": "Ингредиенты должны быть уникальными!"}
            )

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один тэг."
            )

        for tag_data in tags:
            tag_id = tag_data.id
            try:
                Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {"tag": f"Тэг с ID {tag_id} не существует."}
                )

        tag_ids = [data.id for data in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {"tag": "Тэги должны быть уникальными!"}
            )

        return tags

    def to_representation(self, instance):
        representation = super(
            RecipeSerializer, self).to_representation(instance)
        representation["author"] = UserSerializer(
            instance.author, context=self.context
        ).data

        representation["tags"] = TagSerializer(
            instance.tags.all(), many=True
        ).data

        ingredients = instance.recipes.all()
        representation["ingredients"] = IngredientRecipeSerializer(
            ingredients, many=True
        ).data

        return representation

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.favorites.filter(id=user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.shopping_cart.filter(id=user.id).exists()
        return False

    def process_ingredients(self, instance, ingredients_data):
        instance.recipes.all().delete()
        ingredient_recipes = [
            IngredientRecipe(
                recipe=instance,
                ingredient_id=ingredient_data["id"],
                amount=ingredient_data["amount"]
            ) for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredient_recipes)

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.process_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        instance = super().update(instance, validated_data)
        if tags_data:
            instance.tags.set(tags_data)
        instance.recipes.all().delete()
        self.process_ingredients(instance, ingredients_data)
        return instance


class UserSubscriptionSerializer(serializers.ModelSerializer,
                                 IsSubscribedMixin):
    recipes = SimplifiedRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def to_representation(self, instance):
        representation = super(
            UserSubscriptionSerializer,
            self).to_representation(instance)
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")

        if recipes_limit and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
            representation["recipes"] = (
                representation["recipes"][:recipes_limit]
            )

        return representation
