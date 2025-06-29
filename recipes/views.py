# Стандартные библиотеки
from http import HTTPStatus
from io import BytesIO

# Сторонние библиотеки
from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.crypto import get_random_string
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Наши (локальные) импорты
from .filters import IngredientFilter
from .models import Recipe, Ingredient, Favorite, ShoppingCart
from .paginations import RecipePagination
from .serializers.ingredient import IngredientSerializer
from .serializers.other_serializers import FavoriteSerializer, ShoppingCartSerializer
from .serializers.recipe_read import RecipeReadSerializer
from .serializers.recipe_write import RecipeWriteSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = [DjangoFilterBackend]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    pagination_class = RecipePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author"]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "shopping_cart",
            "download_shopping_cart",
        ]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(
                {"detail": "У вас нет разрешения на редактирование рецепта."},
                status=HTTPStatus.FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(
                {"detail": "Вы не можете удалить чужой рецепт."},
                status=HTTPStatus.FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_in_shopping_cart = self.request.query_params.get("is_in_shopping_cart")
        if is_in_shopping_cart is not None and user.is_authenticated:
            queryset = (
                queryset.filter(shoppingcart__user=user)
                if is_in_shopping_cart == "1"
                else queryset.exclude(shoppingcart__user=user)
            )

        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited is not None and user.is_authenticated:
            queryset = (
                queryset.filter(favorite__user=user)
                if is_favorited == "1"
                else queryset.exclude(favorite__user=user)
            )

        return queryset

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        short_code = get_random_string(6)
        short_link = f"{settings.BASE_URL}/short/{short_code}"
        return Response({"short-link": short_link}, status=HTTPStatus.OK)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            data = {"user": request.user.id, "recipe": recipe.id}
            serializer = FavoriteSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                serializer.to_representation(instance),
                status=HTTPStatus.CREATED,
            )
        favorite_qs = Favorite.objects.filter(user=request.user, recipe=recipe)
        if favorite_qs.exists():
            favorite_qs.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            {"error": "Этот рецепт отсутствует в избранном."},
            status=HTTPStatus.BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            data = {"user": request.user.id, "recipe": recipe.id}
            serializer = ShoppingCartSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(
                serializer.to_representation(instance),
                status=HTTPStatus.CREATED,
            )
        cart_qs = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        if cart_qs.exists():
            cart_qs.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            {"error": "Этот рецепт отсутствует в корзине."},
            status=HTTPStatus.BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"error": "Необходима авторизация."},
                status=HTTPStatus.UNAUTHORIZED,
            )

        shopping_cart = ShoppingCart.objects.filter(user=user)

        if not shopping_cart.exists():
            return Response(
                {"error": "Корзина покупок пуста."},
                status=HTTPStatus.BAD_REQUEST,
            )

        ingredients = shopping_cart.values(
            "recipe__ingredients__name", "recipe__ingredients__measurement_unit"
        ).annotate(amount=Sum("recipe__recipeingredient__amount"))

        lines = ["Список покупок:\n"]
        for item in ingredients:
            line = (
                f"{item['recipe__ingredients__name']} "
                f"({item['recipe__ingredients__measurement_unit']}) "
                f"— {item['amount']}"
            )
            lines.append(line)
        content = "\n".join(lines)

        # Create a BytesIO object with the encoded content
        file_obj = BytesIO(content.encode("utf-8"))

        response = FileResponse(
            file_obj,
            as_attachment=True,
            filename="shopping_list.txt",
            content_type="text/plain; charset=utf-8",
        )
        return response
