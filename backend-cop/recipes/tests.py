from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Ingredient, Favorite, ShoppingCart

User = get_user_model()


class RecipeAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.ingredient = Ingredient.objects.create(
            name="Сахар",
            measurement_unit="граммы"
        )

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Тестовый рецепт",
            description="Описание рецепта",
            cooking_time=15,
        )
        self.recipe.ingredients.add(
            self.ingredient, through_defaults={"amount": 100}
        )
        self.client.login(username="testuser", password="password")

    def test_recipe_list(self):
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_add_to_favorite(self):
        response = self.client.post(
            f"/api/recipes/{self.recipe.id}/favorite/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Favorite.objects.filter(user=self.user, recipe=self.recipe)
            .exists()
        )

    def test_remove_from_favorite(self):
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.delete(
            f"/api/recipes/{self.recipe.id}/unfavorite/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Favorite.objects.filter(user=self.user, recipe=self.recipe)
            .exists()
        )

    def test_add_to_shopping_cart(self):
        response = self.client.post(
            f"/api/recipes/{self.recipe.id}/add_to_shopping_cart/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ShoppingCart.objects.filter(user=self.user, recipe=self.recipe)
            .exists()
        )

    def test_remove_from_shopping_cart(self):
        ShoppingCart.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.delete(
            f"/api/recipes/{self.recipe.id}/remove_from_shopping_cart/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            ShoppingCart.objects.filter(user=self.user, recipe=self.recipe)
            .exists()
        )

    def test_ingredient_list(self):
        response = self.client.get("/api/ingredients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_search_ingredient(self):
        response = self.client.get("/api/ingredients/?name=Са")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)
        self.assertEqual(response.data["results"][0]["name"], "Сахар")
