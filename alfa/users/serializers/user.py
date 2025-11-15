"""
Serializers для аутентификации и управления пользователями
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers.business import BusinessSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer для отображения информации о пользователе
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_email_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_email_verified']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer для регистрации нового пользователя
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        """
        Проверка совпадения паролей
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают"
            })
        return attrs
    
    def create(self, validated_data):
        """
        Создание нового пользователя
        """
        # Удаляем password_confirm, он не нужен для создания
        validated_data.pop('password_confirm')
        
        # Создаем пользователя
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer для авторизации пользователя
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Проверка credentials пользователя
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Аутентификация пользователя
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # В Django authenticate username - это email в нашем случае
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Неверный email или пароль',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Аккаунт деактивирован',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Email и пароль обязательны',
                code='authorization'
            )


class TokenSerializer(serializers.Serializer):
    """
    Serializer для возврата JWT токенов
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)
    
    def create(self, validated_data):
        """
        Генерация JWT токенов для пользователя
        """
        user = validated_data.get('user')
        refresh = RefreshToken.for_user(user)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer для полного профиля пользователя с бизнесами
    """
    businesses = BusinessSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_email_verified', 
                  'date_joined', 'businesses']
        read_only_fields = ['id', 'email', 'date_joined', 'is_email_verified']

