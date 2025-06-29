from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import User, Subscription


class SubscriptionAPITestCase(APITestCase):
    def setUp(self):
        """Создание тестовых данных."""
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
            email="testuser@example.com",
        )
        self.author = User.objects.create_user(
            username="author",
            password="password",
            email="author@example.com",
        )
        # Создаем токен для self.user
        token_obj = Token.objects.create(user=self.user)
        self.auth_token = token_obj.key
        # Привязываем клиента к этому токену (авторизуем)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.auth_token}"
        )

    def test_subscribe(self):
        """Тест подписки на автора."""
        response = self.client.post(
            f"/api/users/{self.author.id}/subscribe/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user, author=self.author
            ).exists()
        )

    def test_subscribe_to_self(self):
        """Тест попытки подписки на самого себя."""
        response = self.client.post(
            f"/api/users/{self.user.id}/subscribe/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Вы не можете подписаться на самого себя.",
        )

    def test_logout(self):
        """Тест выхода пользователя с использованием DRF-токена."""
        response = self.client.post("/api/auth/token/logout/")
        self.assertEqual(response.status_code, 204)
        # После удаления токена, повторный запрос уже будет неавторизован
        response2 = self.client.post(
            f"/api/users/{self.author.id}/subscribe/"
        )
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list(self):
        """Тест получения списка пользователей."""
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 200)
        for user in response.data["results"]:
            self.assertIn("avatar", user)

    def test_pagination_with_limit(self):
        for i in range(5):
            User.objects.create_user(
                username=f"user{i}",
                password="password",
                email=f"user{i}@example.com",
            )

        # Отправляем запрос с параметром limit=1
        response = self.client.get("/api/users/?limit=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Отправляем запрос с параметром limit=3
        response = self.client.get("/api/users/?limit=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
