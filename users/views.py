from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

from .serializers import RegisterSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.

    Creates a new user account with email, username, password, and phone number.
    Returns JWT tokens upon successful registration.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Регистрация пользователя",
        description=(
            "Создает новый аккаунт пользователя. "
            "Требуется уникальный email, имя пользователя, пароль и номер телефона. "
            "После успешной регистрации возвращаются JWT токены для аутентификации."
        ),
        tags=["Auth"],
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Успешная регистрация. Возвращает JWT токены.",
                examples=[
                    OpenApiExample(
                        "Successful registration response",
                        summary="Успешная регистрация",
                        description="Пример ответа при успешной регистрации",
                        value={
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Ошибка валидации данных",
                examples=[
                    OpenApiExample(
                        "Validation error response",
                        summary="Ошибка валидации",
                        description="Пример ответа при ошибках валидации",
                        value={
                            "email": ["Введите правильный адрес электронной почты."],
                            "password": ["Пароль должен содержать не менее 8 символов."],
                            "phone_number": ["Неверный формат номера. Используйте 87777777777 или +77777777777"]
                        },
                        response_only=True
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Registration request",
                summary="Пример запроса на регистрацию",
                description="Пример тела запроса для регистрации нового пользователя",
                value={
                    "email": "user@example.com",
                    "username": "newuser",
                    "password": "securepassword123",
                    "phone_number": "87771234567"
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        """
        Register a new user.

        Args:
            request: HTTP request with user registration data

        Returns:
            Response: JWT tokens or validation errors
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Сразу генерируем токены после регистрации (опционально)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
