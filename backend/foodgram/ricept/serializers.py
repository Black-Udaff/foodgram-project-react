from datetime import datetime
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
import webcolors

from .models import Tag, Ingredient


User = get_user_model()


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