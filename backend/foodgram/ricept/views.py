from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from .models import Tag, Ingredient
from .serializers import TagSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class TagViewSet(ListModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]