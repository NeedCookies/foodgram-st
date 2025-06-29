# Сторонние библиотеки
from rest_framework import serializers

# Наши (локальные) импорты
from users.serializers import UserSerializer
from ..fields import Base64ImageField
from ..models import Recipe


class RecipeReadSerializer(serializers.ModelSerializer):
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
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.favorite_set.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.shoppingcart_set.filter(user=request.user).exists()
        )

    def get_ingredients(self, obj):
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