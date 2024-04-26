from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet,
                    RecipeViewSet, CustomUserViewSet)

router = routers.DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', CustomUserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]