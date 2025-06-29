# Сторонние библиотеки
from rest_framework import serializers

# Наши (локальные) импорты
from ..models import Favorite, ShoppingCart


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        recipe = instance.recipe
        request = self.context.get("request")
        return {
            "id": recipe.id,
            "name": recipe.name,
            "image": (
                request.build_absolute_uri(recipe.image.url)
                if request
                else recipe.image.url
            ),
            "cooking_time": recipe.cooking_time,
        }


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        recipe = instance.recipe
        request = self.context.get("request")
        return {
            "id": recipe.id,
            "name": recipe.name,
            "image": (
                request.build_absolute_uri(recipe.image.url)
                if request
                else recipe.image.url
            ),
            "cooking_time": recipe.cooking_time,
        }
