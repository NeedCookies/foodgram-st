import re
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Subscription
from .fields import Base64ImageField
from constants import (
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_FIRSTNAME,
    MAX_LENGTH_LASTNAME,
    ERROR_MESSAGES
)


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not (email and password):
            raise serializers.ValidationError(
                "Требуется email и password",
                code="authorization",
            )
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError(
                "Неверные учётные данные",
                code="authorization",
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Пользователь деактивирован",
                code="authorization",
            )
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.subscribers.filter(user=request.user).exists()
        )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=MAX_LENGTH_FIRSTNAME,
        error_messages={
            "required": ERROR_MESSAGES["first_name_required"],
            "blank": ERROR_MESSAGES["first_name_blank"],
            "max_length": ERROR_MESSAGES["first_name_max_length"],
        },
    )
    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=MAX_LENGTH_LASTNAME,
        error_messages={
            "required": ERROR_MESSAGES["last_name_required"],
            "blank": ERROR_MESSAGES["last_name_blank"],
            "max_length": ERROR_MESSAGES["last_name_max_length"],
        },
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        error_messages={
            "max_length": ERROR_MESSAGES["username_max_length"],
        },
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]

    def validate_username(self, value):
        pattern = r'^[\w.@+-]+$'
        if not re.match(pattern, value):
            raise ValidationError("Неверный формат username.")
        if value.lower() == 'me':
            raise ValidationError("Использовать 'me' как username запрещено.")
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError("Такой username уже зарегистрирован.")
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "user", "author"]

    def to_representation(self, instance):
        author = instance.author
        return {
            "subscriber_id": instance.user.id,
            "author_id": author.id,
            "author_email": author.email,
        }
