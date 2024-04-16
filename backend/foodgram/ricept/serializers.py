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
    name =  serializers.CharField(read_only=True,)
    measurement_unit =  serializers.CharField(read_only=True,)
    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient', write_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient_Recipe
        fields = ('id', 'amount')


    def to_representation(self, instance):
        representation = super(IngredientRecipeSerializer, self).to_representation(instance)
        ingredient_representation = representation.pop('ingredient')
        # Объединяем данные ингредиента с данными количества в один словарь
        return {
            "id": ingredient_representation['id'],
            "name": ingredient_representation['name'],
            "measurement_unit": ingredient_representation['measurement_unit'],
            "amount": representation['amount']
        }

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
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeSerializer(many=True, )
    image = Base64ImageField(required=False, allow_null=True)
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
        representation['tags'] = TagSerializer(instance.tags.all(), many=True).data

        representation['ingredients'] = '1'


        return representation
    



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
                ingredient=ingredient_data['ingredient'],  # Ensure your model and serializer handle this correctly
                amount=ingredient_data['amount']
        )

        return recipe
            

    # def validate_year(self, value):
    #     print(datetime.now().year)
    #     if value > datetime.now().year:
    #         raise serializers.ValidationError('произведение еще не вышло')
    #     return value
