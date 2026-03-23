from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .views import RegisterView

# Добавляем документацию к JWT endpoints
TokenObtainPairView.__doc__ = "JWT аутентификация. Возвращает access и refresh токены."
TokenRefreshView.__doc__ = "Обновление access токена с помощью refresh токена."

urlpatterns = [
    # Регистрация
    path('auth/register/', RegisterView.as_view(), name='auth_register'),

    # Логин (получение пары access/refresh токенов)
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Обновление access токена через refresh
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
