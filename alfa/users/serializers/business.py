"""
Serializers для управления бизнесом
"""
from rest_framework import serializers
from users.models import Business, BusinessProfile


class BusinessSerializer(serializers.ModelSerializer):
    """
    Базовый serializer для информации о бизнесе (список)
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'description', 'status', 
                  'email', 'city', 'owner_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner_email', 'created_at', 'updated_at']


class BusinessCreateSerializer(serializers.ModelSerializer):
    """
    Serializer для создания нового бизнеса
    """
    
    class Meta:
        model = Business
        fields = ['name', 'business_type', 'description', 'email', 'city']
        extra_kwargs = {
            'name': {'required': True},
            'business_type': {'required': True},
        }
    
    def validate_name(self, value):
        """Проверка уникальности названия для текущего пользователя"""
        user = self.context['request'].user
        if Business.objects.filter(owner=user, name=value).exists():
            raise serializers.ValidationError(
                "У вас уже есть бизнес с таким названием"
            )
        return value
    
    def create(self, validated_data):
        """Создание бизнеса с автоматической привязкой к владельцу"""
        user = self.context['request'].user
        business = Business.objects.create(owner=user, **validated_data)
        
        # Автоматически создаем профиль бизнеса
        BusinessProfile.objects.create(business=business)
        
        return business


class BusinessUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer для обновления информации о бизнесе
    """
    
    class Meta:
        model = Business
        fields = ['name', 'business_type', 'description', 'email', 'city', 'status']
    
    def validate_name(self, value):
        """Проверка уникальности названия при обновлении"""
        user = self.context['request'].user
        business_id = self.instance.id if self.instance else None
        
        existing = Business.objects.filter(
            owner=user, 
            name=value
        ).exclude(id=business_id)
        
        if existing.exists():
            raise serializers.ValidationError(
                "У вас уже есть бизнес с таким названием"
            )
        return value


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Serializer для профиля бизнеса
    """
    
    class Meta:
        model = BusinessProfile
        fields = ['employees_count', 'business_context', 'ai_preferences', 'updated_at']
        read_only_fields = ['updated_at']


class BusinessDetailSerializer(serializers.ModelSerializer):
    """
    Детальный serializer для бизнеса с профилем
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    profile = BusinessProfileSerializer(read_only=True)
    
    class Meta:
        model = Business
        fields = [
            'id', 'name', 'business_type', 'description', 'status',
            'email', 'city', 'owner_email', 'owner_name',
            'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner_email', 'owner_name', 'created_at', 'updated_at']