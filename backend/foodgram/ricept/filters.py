import django_filters
from .models import Ingredient, Recipe

class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']




class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(method='get_favorited')
    is_in_shopping_cart = django_filters.CharFilter(method='filter_is_in_shopping_cart')
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')

    def get_favorited(self, queryset, name, value):
        if value == '1':
            return queryset.filter(favorites=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1':
            return queryset.filter(shopping_cart=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']