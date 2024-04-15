import base64
from datetime import datetime
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.relations import SlugRelatedField
import webcolors

from .models import Tag, Ingredient, Recipe, Ingredient_Recipe


User = get_user_model()

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
# class Hex2NameColor(serializers.Field):
#     def to_representation(self, value):
#         return value

#     def to_internal_value(self, data):
#         try:
#             data = webcolors.hex_to_name(data)
#         except ValueError:
#             raise serializers.ValidationError('Для этого цвета нет имени')
#         return data


class TagSerializer(serializers.ModelSerializer):
    # color = Hex2NameColor()
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    # color = Hex2NameColor()
    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = Ingredient_Recipe
        fields = ('ingredient_id', 'amount')

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name"
        )

class RecipeSerializer(serializers.ModelSerializer):
    # genre = serializers.SlugRelatedField(
    #     many=True, slug_field='slug', queryset=Genre.objects.all()
    # )
    # category = SlugRelatedField(
    #     slug_field='slug', queryset=Category.objects.all()
    # )
    # description = serializers.CharField(required=False, allow_blank=True)
    # rating = serializers.FloatField(read_only=True)
    # tags = serializers.SlugRelatedField(
    #     many=True,
    #     slug_field='slug',
    #     queryset=Tag.objects.all()
    # )
    # ingredients = IngredientRecipeSerializer(many=True, source='ingredient_recipe_set')
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    class Meta:
        model = Recipe
        fields = '__all__'
        

    def to_representation(self, instance):
        representation = super(RecipeSerializer, self).to_representation(
            instance
        )

        representation['author'] = UserSerializer(instance.author).data

    #     if instance.category:
    #         representation['category'] = CategorySerializer(
    #             instance.category
    #         ).data

        return representation

    # def validate_year(self, value):
    #     print(datetime.now().year)
    #     if value > datetime.now().year:
    #         raise serializers.ValidationError('произведение еще не вышло')
    #     return value
