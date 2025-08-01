from rest_framework import serializers

from users.serializers import UserSerializer
from ..fields import Base64ImageField
from ..models import Recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для чтения и отображения рецептов. """
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id", "author", "name", "image", "text", "cooking_time",
            "is_favorited", "is_in_shopping_cart", "ingredients", "created_at",
        ]

    def get_is_favorited(self, obj):
        """
        Определяет, находится ли рецепт в избранном у текущего пользователя.
        Возвращает True, если пользователь авторизован и добавил рецепт в избранное.
        """
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.favorite_set.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет наличие рецепта в корзине покупок пользователя.
        Возвращает True, если пользователь авторизован и рецепт добавлен в корзину.
        """
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.shoppingcart_set.filter(user=request.user).exists()
        )

    def get_ingredients(self, obj):
        """ Формирует список ингредиентов рецепта с их количеством. """
        recipeingredients = (
            obj.recipeingredient_set
               .select_related("ingredient")
        )
        return [
            {
                "id": ri.ingredient.id,
                "name": ri.ingredient.name,
                "measurement_unit": ri.ingredient.measurement_unit,
                "amount": ri.amount,
            }
            for ri in recipeingredients
        ] 