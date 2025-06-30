from rest_framework import serializers

from ..models import Favorite, ShoppingCart


def get_recipe_relation_serializer(model):
    """
    Фабричная функция для создания сериализаторов,
    связывающих пользователя с рецептом (например, избранное или корзина).
    Принимает модель связи и возвращает специализированный сериализатор.
    """
    class RecipeRelationSerializer(serializers.ModelSerializer):
        """
        Сериализатор для отображения связи пользователя с рецептом.
        Используется для избранных рецептов и списка покупок.
        """
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

#: Сериализатор для избранных рецептов пользователя
FavoriteSerializer = get_recipe_relation_serializer(Favorite)

#: Сериализатор для рецептов в корзине покупок пользователя
ShoppingCartSerializer = get_recipe_relation_serializer(ShoppingCart) 