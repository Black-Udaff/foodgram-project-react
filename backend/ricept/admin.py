from django.contrib import admin

from .models import Tag, Ingredient, Recipe, Subscription


@admin.register(Tag)
class TitleAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class TitleAdmin(admin.ModelAdmin):
    pass


class ShoppingCartInline(admin.TabularInline):
    model = Recipe.shopping_cart.through
    extra = 1
    verbose_name = 'User with Recipe in Shopping Cart'
    verbose_name_plural = 'Users with Recipe in Shopping Carts'
    fk_name = 'recipe'
    raw_id_fields = ('user',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    inlines = [ShoppingCartInline]


@admin.register(Subscription)
class TitleAdmin(admin.ModelAdmin):
    pass
