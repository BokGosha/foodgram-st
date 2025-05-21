from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from djoser.serializers import SetPasswordSerializer
from django_filters.rest_framework import DjangoFilterBackend

from .services import shopping_cart
from .filters import RecipeFilter
from .permissions import IsOwnerOrReadOnly
from users.models import User, Follow
from recipes.models import (
    Recipe, Ingredient,
    Favorite, ShoppingCart, RecipeShortLink)
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    IngredientSerializer, RecipeListSerializer,
    RecipeWriteSerializer, RecipeMinifiedSerializer,
    SetAvatarSerializer, FollowSerializer)
from .paginations import CustomPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(['post'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(
                'Пароль успешно изменен',
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data,
                context={'request': request, 'author': author},
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {'detail': [
                    'Объект не найден'
                ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if Follow.objects.filter(author=author, user=user).exists():
            Follow.objects.get(author=author).delete()
            return Response(
                'Успешная отписка',
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {'detail': [
                'Объект не найден'
            ]
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follows = Follow.objects.filter(
            user=self.request.user).order_by('author__username')
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(pages,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['put', 'delete'],
            url_path='me/avatar', url_name='user-avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'avatar': [
                        'Это поле обязательно'
                    ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = SetAvatarSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)

            if user.avatar:
                user.avatar.delete()

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        elif request.method == 'DELETE':
            if not user.avatar:
                return Response(
                    {'detail': [
                        'Аватар уже отсутствует'
                    ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link, code = RecipeShortLink.objects.get_or_create(
            recipe=recipe)
        return Response({
            'short-link': request.build_absolute_uri(
                f'/s/{short_link.code}/')
        })

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if Favorite.objects.filter(
                    author=request.user,
                    recipe=recipe).exists():
                return Response(
                    {'detail': [
                        'Рецепт уже в избранном'
                    ]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(author=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                author=request.user,
                recipe=recipe
            ).first()
            if not favorite:
                return Response(
                    {'detail': [
                        'Рецепта нет в избранном'
                    ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    author=request.user,
                    recipe=recipe).exists():
                return Response(
                    {'detail': [
                        'Рецепт уже в списке покупок'
                    ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(author=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(
                author=request.user,
                recipe=recipe
            ).first()
            if not cart_item:
                return Response(
                    {'detail': [
                        'Рецепта нет в списке покупок'
                    ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        author = User.objects.get(id=self.request.user.pk)
        if author.shopping_cart.exists():
            return shopping_cart(self, request, author)

        return Response(
            'Список покупок пуст.',
            status=status.HTTP_404_NOT_FOUND,
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class ShortLinkRedirect(views.APIView):
    def get(self, request, code):
        short_link = get_object_or_404(RecipeShortLink, code=code)

        return redirect(
            f'http://{request.get_host()}/recipes/{short_link.recipe.id}/'
        )
