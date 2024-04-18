from django.shortcuts import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tag, Ingredient, Recipe, Subscription, User
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from .filters import IngredientFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from djoser.views import UserViewSet as DjoserUserViewSet



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
        



# class FolowViewSet(ModelViewSet):
#     serializer_class = FollowSerializer
#     queryset = Follow.objects.all()
#     permission_classes = [
#         IsAuthenticated,
#     ]
#     filter_backends = (SearchFilter,)
#     search_fields = ('following__username',)

#     def get_queryset(self):
#         user = self.request.user
#         return user.follower.all()

#     def perform_create(self, serializer):
#         if serializer.validated_data.get('following') == self.request.user:
#             raise ValidationError('Нельзя подписаться на самого себя.')
#         serializer.save(user=self.request.user)

class CustomUserViewSet(DjoserUserViewSet):
    @action(detail=True, methods=['post', 'delete'], url_path='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **pk):
        print(pk)
        if request.method == 'POST':
            if request.user.id == int(pk['id']):
                return Response({'error': 'You cannot subscribe to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

            target_user = get_object_or_404(User, pk=pk['id'])
            # Проверяем, есть ли уже такая подписка
            if Subscription.objects.filter(subscriber=request.user, subscribed_to=target_user).exists():
                return Response({'error': 'You are already subscribed to this user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Создаем новую подписку
            Subscription.objects.create(subscriber=request.user, subscribed_to=target_user)
            return Response({'message': 'Subscription successful.'}, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            if request.user.id == int(pk['id']):
                return Response({'error': 'You cannot unsubscribe from yourself.'}, status=status.HTTP_400_BAD_REQUEST)

            target_user = get_object_or_404(User, pk=pk['id'])
            subscription = Subscription.objects.filter(subscriber=request.user, subscribed_to=target_user).first()
            if subscription:
                subscription.delete()
                return Response({'message': 'Unsubscription successful.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'You are not subscribed to this user.'}, status=status.HTTP_404_NOT_FOUND)

