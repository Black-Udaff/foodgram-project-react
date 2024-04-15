from django.contrib import admin


from .models import Tag, Ingredient


@admin.register(Tag)
class TitleAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class TitleAdmin(admin.ModelAdmin):
    pass
