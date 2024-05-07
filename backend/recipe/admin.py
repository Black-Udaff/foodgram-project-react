from django.contrib import admin

from .models import Ingredient, Recipe, Subscription, Tag


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'subscribed_to')
    search_fields = ('subscriber', 'subscribed_to')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text',
                    'pub_date', 'author',
                    'get_favorite_count')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)
    exclude = ('tags',)
    list_filter = ('name', 'author__username', 'tags__name')

    def get_favorite_count(self, obj):
        return obj.subscriptions.count()

    get_favorite_count.short_description = 'Favorites'
