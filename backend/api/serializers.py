import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from users.models import User, Follow
from recipes.models import (
    RecipeShortLink,
    Recipe,
    Ingredient,
    RecipeIngredient,
)


MAX_VALUE = 32_000
MIN_VALUE = 1


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        extra_kwargs = {'is_subscribed': {'read_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and (user.follower.filter(author=obj).exists())
        )


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(
        source='author.email',
    )

    id = serializers.ReadOnlyField(
        source='author.id',
    )

    username = serializers.ReadOnlyField(
        source='author.username',
    )

    first_name = serializers.ReadOnlyField(
        source='author.first_name',
    )

    last_name = serializers.ReadOnlyField(
        source='author.last_name',
    )

    avatar = serializers.SerializerMethodField()

    is_subscribed = serializers.SerializerMethodField()

    recipes = serializers.SerializerMethodField()

    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        return True

    def get_avatar(self, obj):
        request = self.context['request']
        if obj.author.avatar:
            return (
                request.build_absolute_uri(obj.author.avatar.url)
                if request
                else obj.author.avatar.url
            )
        return None

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context['request'].user

        if user.follower.filter(author=author).exists():
            raise ValidationError(
                {'detail': ['Вы уже подписаны на этого пользователя!']},
                code=status.HTTP_400_BAD_REQUEST,
            )

        if user == author:
            raise ValidationError(
                {'detail': ['Невозможно подписаться на себя!']},
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )

    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )

    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )

    is_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and (user.favorite.filter(recipe=obj).exists())
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and (
            user.shopping_cart.filter(recipe=obj).exists()
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    amount = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(
        many=True,
        write_only=True,
    )

    image = Base64ImageField()

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    cooking_time = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )

    def validate_ingredients(self, value):
        if not value:
            serializers.ValidationError(
                {'ingredients': [
                    'Необходимо указать хотя бы один ингредиент.']},
            )

        ingredients = set()
        for item in value:
            ingredient = get_object_or_404(Ingredient, name=item['id'])
            if ingredient in ingredients:
                raise ValidationError(
                    {'ingredients': ['Ингридиенты повторяются!']},
                )

            ingredients.add(ingredient)
        return value

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    def add_ingredients(self, ingredients, model):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        if ingredients is None or ingredients == []:
            raise serializers.ValidationError(
                {'ingredients': [
                    'Необходимо указать хотя бы один ингредиент!']},
            )
        recipe = super().create(validated_data)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is None or ingredients == []:
            raise serializers.ValidationError(
                {'ingredients': [
                    'Необходимо указать хотя бы один ингредиент!']},
            )
        instance.ingredients.clear()
        self.add_ingredients(ingredients, instance)
        return super().update(instance, validated_data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image',
        )
        read_only_fields = fields


class RecipeShortLinkSerializer(serializers.ModelSerializer):
    short_link = serializers.SerializerMethodField()

    class Meta:
        model = RecipeShortLink
        fields = ('short_link',)

    def get_short_link(self, obj):
        request = self.context.get('request')
        return (
            request.build_absolute_uri(f'/s/{obj.code}/') if request else None
        )
