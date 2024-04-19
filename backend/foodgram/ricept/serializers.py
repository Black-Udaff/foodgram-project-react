import base64
from datetime import datetime
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
import webcolors

from .models import Tag, Ingredient, Recipe, Ingredient_Recipe, Subscription


User = get_user_model()

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    # color = Hex2NameColor()
    name =  serializers.CharField(read_only=True,)
    measurement_unit =  serializers.CharField(read_only=True,)
    amount = serializers.IntegerField(required=False)
    id = serializers.IntegerField()
    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)
    id = serializers.IntegerField(source='ingredient.id', read_only=True)

    class Meta:
        model = Ingredient_Recipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name",
                  "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        print(obj)
        print(self)
        # Проверка, аутентифицирован ли пользователь и добавлен ли рецепт в избранное
        user = self.request
        if user.is_authenticated:
            return Subscription.objects.filter(subscriber=user, subscribed_to=obj).exists()
        return False

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientSerializer(many=True, )
    image = Base64ImageField(required=False, allow_null=True)
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = '__all__'
    

    

    def to_representation(self, instance):
        representation = super(RecipeSerializer, self).to_representation(
            instance
        )

        representation['author'] = UserSerializer(instance.author).data

    #     if instance.category:
        representation['tags'] = TagSerializer(instance.tags.all(), many=True).data

        ingredients = instance.recipe.all()
        representation['ingredients'] = IngredientRecipeSerializer(ingredients, many=True).data


        return representation
    

    def get_is_favorited(self, obj):
        # Проверка, аутентифицирован ли пользователь и добавлен ли рецепт в избранное
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorites.filter(id=user.id).exists()
        return False
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_cart.filter(id=user.id).exists()
        return False



    def create(self, validated_data):
        print(validated_data)
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        print(ingredients_data)
        recipe.tags.set(tags_data)  # Set the tags using the set method

        for ingredient_data in ingredients_data:
            print(ingredient_data)
            Ingredient_Recipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],  # Ensure your model and serializer handle this correctly
                amount=ingredient_data['amount']
        )

        return recipe
            

    # def validate_year(self, value):
    #     print(datetime.now().year)
    #     if value > datetime.now().year:
    #         raise serializers.ValidationError('произведение еще не вышло')
    #     return value


# class FollowSerializer(serializers.ModelSerializer):
#     user = serializers.SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all(),
#         default=serializers.CurrentUserDefault())
#     following = serializers.SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all())

#     class Meta:
#         model = Follow
#         fields = '__all__'
#         validators = (
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'following'),
#                 message=('Подписка на автора оформлена ранее!')
#             ),
#         )