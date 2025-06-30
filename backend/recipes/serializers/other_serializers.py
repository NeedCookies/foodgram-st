from rest_framework import serializers

from ..models import Favorite, ShoppingCart


def get_recipe_relation_serializer(model):
    class RecipeRelationSerializer(serializers.ModelSerializer):
        """Универсальный сериализатор для связи пользователя с рецептом (избранное, корзина)."""
        class Meta:
            fields = ["user", "recipe"]

        def to_representation(self, instance):
            recipe = instance.recipe
            request = self.context.get("request")
            return {
                "id": recipe.id,
                "name": recipe.name,
                "image": request.build_absolute_uri(recipe.image.url)
                if request else recipe.image.url,
                "cooking_time": recipe.cooking_time,
            }
    
    setattr(RecipeRelationSerializer.Meta, 'model', model)
    return RecipeRelationSerializer

FavoriteSerializer = get_recipe_relation_serializer(Favorite)
ShoppingCartSerializer = get_recipe_relation_serializer(ShoppingCart) 