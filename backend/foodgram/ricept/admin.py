from django.contrib import admin


from .models import Tag


@admin.register(Tag)
class TitleAdmin(admin.ModelAdmin):
    pass
