# Сторонние библиотеки
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# Наши (локальные) импорты
from constants import MIN_COOKING_TIME
from ..models import Recipe, RecipeIngredient, Ingredient
from ..fields import Base64ImageField


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "text", "cooking_time", "ingredients")

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method in ("PUT", "PATCH"):
            if (
                "ingredients" in self.initial_data
                and not self.initial_data["ingredients"]
            ):
                raise ValidationError(
                    {
                        "ingredients": (
                            "Поле 'ingredients' обязательно "
                            "при обновлении."
                        )
                    }
                )
        return attrs

    def validate_cooking_time(self, value):
        if value < MIN_COOKING_TIME:
            raise ValidationError(
                f"Время готовки минимум {MIN_COOKING_TIME} минут."
            )
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError(
                {"image": "Поле 'image' не может быть пустым."}
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {"ingredients": "Поле 'ingredients' не может быть пустым."}
            )

        unique_ingredient_ids = set()
        for item in value:
            ingredient_id = item["id"]

            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise ValidationError(
                    {
                        "ingredients": (
                            f"Ингредиент с id {ingredient_id} не существует."
                        )
                    }
                )

            if ingredient_id in unique_ingredient_ids:
                raise ValidationError(
                    {
                        "ingredients": (
                            f"Ингредиент с id {ingredient_id} "
                            "указан несколько раз."
                        )
                    }
                )

            unique_ingredient_ids.add(ingredient_id)

        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user,
            **validated_data
        )
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        recipe = super().update(instance, validated_data)
        if ingredients_data:
            recipe.recipeingredient_set.all().delete()
            self._save_ingredients(recipe, ingredients_data)

        return recipe

    def _save_ingredients(self, recipe, ingredients_data):
        recipeingredient_list = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=item["id"]),
                amount=item["amount"]
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipeingredient_list)

    def to_representation(self, instance):
        from .recipe_read import RecipeReadSerializer
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data
