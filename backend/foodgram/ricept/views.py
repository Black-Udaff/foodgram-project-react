import csv
from django.http import HttpResponse
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
from .models import Ingredient_Recipe, Tag, Ingredient, Recipe, Subscription, User
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, UserSerializer, UserSubscriptionSerializer
from .filters import IngredientFilter, RecipeFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Prefetch
from django.contrib.auth import get_user_model


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
    permission_classes = [IsAuthenticatedOrReadOnly]
    # permission_classes = (IsAuthor | IsModerator | IsAdmin,)

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.filterset_class(data=self.request.GET, queryset=queryset, request=self.request)
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
        
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            recipe.shopping_cart.add(request.user)
            return Response({'status': 'recipe added to shopping_cart'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe.shopping_cart.remove(request.user)
            return Response({'status': 'recipe removed from shopping_cart'}, status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=False, methods=['get'], url_path='download_shopping_cart', permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        # Создание HTTP ответа с типом содержимого, соответствующим CSV файлу
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.csv"'

        # Создаем writer объект, который будет использовать для записи в CSV
        writer = csv.writer(response)

        # Заголовки столбцов
        writer.writerow(['Recipe Name', 'Description', 'Cooking Time'])

        # Получаем пользователя
        user = request.user

        # Предположим, что у вас есть модель Recipe, которая связана с моделью Ingredient через промежуточную таблицу
        recipes = Recipe.objects.filter(shopping_cart=user)
        print(recipes)

        # ingredients = {}
        # for recipe in recipes:
        #     for item in recipe.ingredients.all():
        #         name = item.ingredient.name
        #         if name in ingredients:
        #             ingredients[name]['amount'] += item.amount
        #         else:
        #             ingredients[name] = {
        #                 'amount': item.amount,
        #                 'unit': item.ingredient.measurement_unit
        #             }

        # # Запись данных ингредиентов
        # for name, data in ingredients.items():
        #     writer.writerow([name, data['amount'], data['unit']])
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
        # Добавляем текущего пользователя в контекст
        context['user'] = self.request.user
        print(context['user'])
        return context

    
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
            print(subscription)
            if subscription:
                subscription.delete()
                return Response({'message': 'Unsubscription successful.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'You are not subscribed to this user.'}, status=status.HTTP_404_NOT_FOUND)
            

    @action(detail=False, methods=['get'], url_path='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        # Получаем пользователей, на которых подписан текущий пользователь
        following_users = User.objects.filter(followers__subscriber=request.user)
        
        # Применяем пагинацию
        page = self.paginate_queryset(following_users)
        if page is not None:
            serializer = UserSubscriptionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        # Возврат данных без пагинации, если пагинация не настроена (этот кейс должен быть редкостью)
        serializer = UserSubscriptionSerializer(following_users, many=True, context={'request': request})
        return Response(serializer.data)
