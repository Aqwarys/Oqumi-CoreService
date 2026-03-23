from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Creates a new user account with email, username, password, and phone number.
    Password is write-only and will not be included in responses.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Пароль пользователя. Минимум 8 символов."
    )

    email = serializers.EmailField(
        help_text="Адрес электронной почты пользователя. Должен быть уникальным."
    )

    username = serializers.CharField(
        max_length=150,
        help_text="Имя пользователя. Используется для входа в систему."
    )

    phone_number = serializers.CharField(
        max_length=15,
        help_text="Номер телефона пользователя в формате 87777777777 или +77777777777"
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'phone_number')

    def create(self, validated_data):
        """
        Create and return a new user instance.

        Args:
            validated_data (dict): Validated serializer data

        Returns:
            User: Created user instance
        """
        # Используем метод нашего менеджера для корректного хеширования пароля
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', '')
        )
        return user

    def validate_phone_number(self, value):
        """
        Validate phone number format.

        Args:
            value (str): Phone number to validate

        Raises:
            serializers.ValidationError: If phone number format is invalid

        Returns:
            str: Validated phone number
        """
        if not value:
            raise serializers.ValidationError("Номер телефона обязателен")

        if not re.match(r'^(\+7|8)\d{10}$', value):
            raise serializers.ValidationError(
                "Неверный формат номера. Используйте 87777777777 или +77777777777"
            )

        return value
