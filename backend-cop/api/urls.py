# Сторонние библиотеки
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Локальные импорты
from recipes.views import IngredientViewSet, RecipeViewSet
from users.views import AuthTokenView, LogoutView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("ingredients", IngredientViewSet, basename="ingredient")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", AuthTokenView.as_view(), name="token_login"),
    path("auth/token/logout/", LogoutView.as_view(), name="token_logout"),
]
