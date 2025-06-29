# Стандартные библиотеки
import logging
import base64
import uuid

# Сторонние библиотеки
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import check_password
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

# Наши (локальные) импорты
from recipes.models import Recipe
from .models import User, Subscription
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    EmailAuthTokenSerializer,
)
from .paginations import UserPagination

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False, methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        from http import HTTPStatus
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(
        detail=False, methods=["post"],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        old_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response(
                {
                    "error": "Поля 'current_password' "
                             "и 'new_password' обязательны."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not check_password(old_password, user.password):
            return Response(
                {"error": "Текущий пароль указан неверно."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if old_password == new_password:
            return Response(
                {"error": "Новый пароль не должен совпадать с текущим."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["put", "delete"], url_path="me/avatar",
        permission_classes=[IsAuthenticated]
    )
    def update_avatar(self, request):
        if request.method == "PUT":
            avatar_base64 = request.data.get("avatar")
            if not avatar_base64:
                return Response(
                    {"error": "Поле 'avatar' обязательно."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                format_part, imgstr = avatar_base64.split(";base64,")
                ext = format_part.split("/")[-1]
                file_name = f"{uuid.uuid4()}.{ext}"
                request.user.avatar.save(
                    file_name, ContentFile(base64.b64decode(imgstr)), save=True
                )
                return Response(
                    {"avatar": request.build_absolute_uri(
                        request.user.avatar.url)},
                    status=status.HTTP_200_OK,
                )
            except Exception as exc:
                logger.error(f"Ошибка при обновлении аватара: {exc}")
                return Response(
                    {"error": "Не удалось обновить аватар."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        if not request.user.avatar:
            return Response(
                {"detail": "Аватар отсутствует."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        from http import HTTPStatus

        user = request.user
        author = self.get_object()

        if request.method == "DELETE":
            subscription = Subscription.objects.filter(
                user=user, author=author
            )
            if not subscription.exists():
                return Response(
                    {"error": "Вы не подписаны на этого пользователя."},
                    status=HTTPStatus.BAD_REQUEST,
                )
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        if user == author:
            return Response(
                {"error": "Вы не можете подписаться на самого себя."},
                status=HTTPStatus.BAD_REQUEST,
            )
        subscription, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            return Response(
                {"error": "Вы уже подписаны на этого пользователя."},
                status=HTTPStatus.BAD_REQUEST,
            )

        recipes_limit = request.query_params.get("recipes_limit")
        try:
            recipes_limit = int(recipes_limit) if recipes_limit else None
        except ValueError:
            recipes_limit = None

        author_data = UserSerializer(author, context={"request": request}).data
        author_data["recipes_count"] = Recipe.objects.filter(
            author=author
        ).count()
        qs = Recipe.objects.filter(author=author)
        if recipes_limit:
            qs = qs[:recipes_limit]
        author_data["recipes"] = [
            {
                "id": r.id,
                "name": r.name,
                "image": request.build_absolute_uri(r.image.url)
                if request else r.image.url,
                "cooking_time": r.cooking_time,
            }
            for r in qs
        ]
        return Response(author_data, status=HTTPStatus.CREATED)

    @action(detail=True, methods=["delete"])
    def unsubscribe(self, request, pk=None):
        user = request.user
        author = self.get_object()
        Subscription.objects.filter(user=user, author=author).delete()
        return Response({"status": "unsubscribed"})

    @action(
        detail=False, methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            subscribers__user=user
        ).annotate(recipes_count=Count("recipes"))

        paginator = UserPagination()
        page = paginator.paginate_queryset(subscriptions, request)
        response_data = []
        recipes_limit = request.query_params.get("recipes_limit")
        try:
            recipes_limit = int(recipes_limit) if recipes_limit else None
        except ValueError:
            recipes_limit = None

        for author in page:
            author_data = UserSerializer(
                author, context={"request": request}
            ).data
            author_data["recipes_count"] = author.recipes_count
            qs = Recipe.objects.filter(author=author)
            if recipes_limit:
                qs = qs[:recipes_limit]
            author_data["recipes"] = [
                {
                    "id": r.id,
                    "name": r.name,
                    "image": request.build_absolute_uri(r.image.url)
                    if request else r.image.url,
                    "cooking_time": r.cooking_time,
                }
                for r in qs
            ]
            response_data.append(author_data)

        return paginator.get_paginated_response(response_data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from http import HTTPStatus

        try:
            Token.objects.get(user=request.user).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        except Token.DoesNotExist:
            return Response(
                {"detail": "Токен для данного пользователя не найден."},
                status=HTTPStatus.BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Ошибка при выходе: {exc}")
            return Response(
                {"detail": str(exc)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


class AuthTokenView(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        from http import HTTPStatus

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"auth_token": token.key}, status=HTTPStatus.OK)
