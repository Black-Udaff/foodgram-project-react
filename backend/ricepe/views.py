import csv

from django.db.models import Sum
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
from .models import (Ingredient, IngredientRecipe, Recipe,
                     Subscription, Tag, User)
from .permissions import CurrentUserOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SimplifiedRecipeSerializer, TagSerializer,
                          UserSubscriptionSerializer)


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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def get_serializer_context(self):

        context = super().get_serializer_context()
        context['user'] = self.request.user
        print(context['user'])
        return context

    def handle_recipe_list_toggle(self, request, pk, list_type):
        recipe = Recipe.objects.filter(pk=pk).first()

        if request.method == 'POST':
            if not recipe:
                return Response({'error': 'Recipe not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            user_list = getattr(recipe, list_type)
            if user_list.filter(id=request.user.id).exists():
                return Response(
                    {'error': f'This recipe is already in {list_type}'},
                    status=status.HTTP_400_BAD_REQUEST)
            user_list.add(request.user)
            serializer = SimplifiedRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if not recipe:
                return Response({'error': 'Recipe not found'},
                                status=status.HTTP_404_NOT_FOUND)
            user_list = getattr(recipe, list_type)
            if not user_list.filter(id=request.user.id).exists():
                return Response(
                    {'error': f'Recipe is not in your {list_type}'},
                    status=status.HTTP_400_BAD_REQUEST)
            user_list.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.handle_recipe_list_toggle(request, pk, 'favorites')

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.handle_recipe_list_toggle(request, pk, 'shopping_cart')

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.csv"')

        writer = csv.writer(response)
        writer.writerow(['Ingredient', 'Total Amount', 'Measurement Unit'])

        user = request.user

        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        for ingredient in ingredients:
            writer.writerow([
                ingredient['ingredient__name'],
                ingredient['total_amount'],
                ingredient['ingredient__measurement_unit']
            ])

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

        else:
            if request.user.id == int(pk['id']):
                return Response({'error': 'You cannot unsubscribe from self.'},
                                status=status.HTTP_400_BAD_REQUEST)

            target_user = get_object_or_404(User, pk=pk['id'])
            subscription = Subscription.objects.filter(
                subscriber=request.user, subscribed_to=target_user).first()
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
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
