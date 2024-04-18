from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tag, Ingredient, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from .filters import IngredientFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class TagViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]


class IngredientViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]
    permission_classes = [IsAuthenticatedOrReadOnly]
    # permission_classes = (IsAuthor | IsModerator | IsAdmin,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            recipe.favorites.add(request.user)
            return Response({'status': 'recipe added to favorites'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe.favorites.remove(request.user)
            return Response({'status': 'recipe removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            recipe.shopping_cart.add(request.user)
            return Response({'status': 'recipe added to shopping_cart'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe.shopping_cart.remove(request.user)
            return Response({'status': 'recipe removed from shopping_cart'}, status=status.HTTP_204_NO_CONTENT)