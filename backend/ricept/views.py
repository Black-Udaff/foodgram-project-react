import csv

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Subscription, Tag, User
from .permissions import CurrentUserOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SimplifiedRecipeSerializer, TagSerializer,
                          UserSubscriptionSerializer)

User = get_user_model()


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]
    permission_classes = [CurrentUserOrAdminOrReadOnly]
    # permission_classes = (IsAuthor | IsModerator | IsAdmin,)

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.filterset_class(data=self.request.GET,
                                         queryset=queryset,
                                         request=self.request)
        if filterset.is_valid():
            queryset = filterset.qs
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def get_serializer_context(self):

        context = super().get_serializer_context()
        # Добавляем текущего пользователя в контекст
        context['user'] = self.request.user
        print(context['user'])
        return context

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()
        if request.method == 'POST':
            if not recipe:
                return Response({'error': 'Recipe not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            if recipe.favorites.filter(id=request.user.id).exists():
                return Response({'error': 'This recipe is already in list'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe.favorites.add(request.user)
            serializer = SimplifiedRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not recipe:
                return Response({'error': 'Recipe not found'},
                                status=status.HTTP_404_NOT_FOUND)
            if not recipe.favorites.filter(id=request.user.id).exists():
                return Response({'error': 'Recipe is not in your favorites'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe.favorites.remove(request.user)
            return Response({'status': 'recipe removed from favorites'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()

        if request.method == 'POST':
            if not recipe:
                return Response({'error': 'Recipe not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            if recipe.shopping_cart.filter(id=request.user.id).exists():
                return Response({'error': 'This recipe is already in list'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe.shopping_cart.add(request.user)
            serializer = SimplifiedRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not recipe:
                return Response({'error': 'Recipe not found'},
                                status=status.HTTP_404_NOT_FOUND)
            if not recipe.shopping_cart.filter(id=request.user.id).exists():
                # Возвращает 400, если рецепт не был в корзине
                return Response({'error': 'Recipe not in shopping cart'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe.shopping_cart.remove(request.user)
            return Response({'status': 'Recipe removed from shopping cart'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.csv"')

        writer = csv.writer(response)
        writer.writerow(['Recipe Name', 'Description', 'Cooking Time'])

        user = request.user

        recipes = Recipe.objects.filter(shopping_cart=user)

        for recipe in recipes:
            writer.writerow([recipe.name, recipe.text, recipe.cooking_time])

        return response


class CustomUserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        print(context['user'])
        return context

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **pk):
        print(pk)
        if request.method == 'POST':
            if request.user.id == int(pk['id']):
                return Response({'error': 'You cannot subscribe to self.'},
                                status=status.HTTP_400_BAD_REQUEST)

            target_user = get_object_or_404(User, pk=pk['id'])
            if Subscription.objects.filter(subscriber=request.user,
                                           subscribed_to=target_user).exists():
                return Response(
                    {'error': 'You are already subscribed to this user.'},
                    status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(subscriber=request.user,
                                        subscribed_to=target_user)
            serializer = UserSubscriptionSerializer(
                target_user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if request.user.id == int(pk['id']):
                return Response({'error': 'You cannot unsubscribe from self.'},
                                status=status.HTTP_400_BAD_REQUEST)

            target_user = get_object_or_404(User, pk=pk['id'])
            subscription = Subscription.objects.filter(
                subscriber=request.user, subscribed_to=target_user).first()
            print(subscription)
            if subscription:
                subscription.delete()
                return Response({'message': 'Unsubscription successful.'},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'You are not subscribed to this user.'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        following_users = User.objects.filter(
            followers__subscriber=request.user)

        page = self.paginate_queryset(following_users)
        if page is not None:
            serializer = UserSubscriptionSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(
            following_users, many=True, context={'request': request})
        return Response(serializer.data)
