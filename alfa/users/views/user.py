"""
Views для аутентификации и управления пользователями
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from users.models import User
from users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    TokenSerializer,
    UserProfileSerializer,
    UserSerializer
)
from users.utils.api_response import APIResponse, format_serializer_errors


class RegisterView(generics.CreateAPIView):
    """
    API endpoint для регистрации нового пользователя
    
    POST /api/auth/register/
    {
        "email": "user@example.com",
        "password": "secure_password",
        "password_confirm": "secure_password",
        "first_name": "Иван",
        "last_name": "Иванов"
    }
    
    Response:
    {
        "access": "...",
        "refresh": "...",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "Иван",
            "last_name": "Иванов"
        }
    }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        user = serializer.save()
        
        # Генерируем JWT токены
        token_serializer = TokenSerializer(data={'user': user})
        token_serializer.is_valid()
        tokens = token_serializer.create({'user': user})
        
        return APIResponse.created(
            data=tokens,
            message="Пользователь успешно зарегистрирован"
        )


class LoginView(APIView):
    """
    API endpoint для авторизации пользователя
    
    POST /api/auth/login/
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    
    Response:
    {
        "access": "...",
        "refresh": "...",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "Иван",
            "last_name": "Иванов"
        }
    }
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return APIResponse.error(
                message="Ошибка авторизации",
                errors=format_serializer_errors(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.validated_data['user']
        
        # Генерируем JWT токены
        token_serializer = TokenSerializer(data={'user': user})
        token_serializer.is_valid()
        tokens = token_serializer.create({'user': user})
        
        return APIResponse.success(
            data=tokens,
            message="Вход выполнен успешно"
        )


class LogoutView(APIView):
    """
    API endpoint для выхода из системы (добавление refresh токена в blacklist)
    
    POST /api/auth/logout/
    {
        "refresh": "refresh_token_here"
    }
    
    Response:
    {
        "message": "Вы успешно вышли из системы"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return APIResponse.validation_error(
                    errors={"refresh": "Refresh token обязателен"},
                    message="Refresh token не предоставлен"
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return APIResponse.success(
                message="Вы успешно вышли из системы"
            )
        except TokenError as e:
            return APIResponse.error(
                message="Невалидный или истекший токен",
                errors={"refresh": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return APIResponse.error(
                message="Ошибка при выходе из системы",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    API endpoint для получения и обновления информации о текущем пользователе
    
    GET /api/auth/me/
    Response:
    {
        "success": true,
        "message": "Профиль пользователя получен",
        "data": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "Иван",
            "last_name": "Иванов",
            "is_email_verified": false,
            "date_joined": "2024-01-01T00:00:00Z",
            "businesses": [...]
        }
    }
    
    PATCH /api/auth/me/
    {
        "first_name": "Новое имя",
        "last_name": "Новая фамилия"
    }
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """Переопределяем GET метод для стандартизированного ответа"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Профиль пользователя получен"
        )
    
    def update(self, request, *args, **kwargs):
        """Переопределяем PATCH/PUT методы для стандартизированного ответа"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        self.perform_update(serializer)
        
        return APIResponse.success(
            data=serializer.data,
            message="Профиль успешно обновлен"
        )


class VerifyTokenView(APIView):
    """
    API endpoint для проверки валидности токена
    
    POST /api/auth/verify/
    {
        "token": "access_token_here"
    }
    
    Response:
    {
        "valid": true,
        "user": {...}
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return APIResponse.success(
            data={
                "valid": True,
                "user": serializer.data
            },
            message="Токен валиден"
        )

