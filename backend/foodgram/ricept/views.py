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
from rest_framework.permissions import IsAuthenticatedOrReadOnly


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