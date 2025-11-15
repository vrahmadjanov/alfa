"""
Serializers для чата и сообщений
"""
from rest_framework import serializers
from chat.models import Conversation, Message
from users.serializers import BusinessSerializer


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer для сообщения
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'role', 'role_display', 'content', 
            'model', 'tokens_used', 'response_time', 'created_at'
        ]
        read_only_fields = ['id', 'role_display', 'model', 'tokens_used', 'response_time', 'created_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer для создания сообщения пользователя
    """
    
    class Meta:
        model = Message
        fields = ['content']
    
    def validate_content(self, value):
        """Валидация содержимого сообщения"""
        if not value or not value.strip():
            raise serializers.ValidationError("Сообщение не может быть пустым")
        
        if len(value) > 4000:
            raise serializers.ValidationError("Сообщение слишком длинное (максимум 4000 символов)")
        
        return value.strip()


class ConversationSerializer(serializers.ModelSerializer):
    """
    Базовый serializer для диалога (список)
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    messages_count = serializers.IntegerField(source='get_messages_count', read_only=True)
    last_message = serializers.SerializerMethodField()
    business_name = serializers.CharField(source='business.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'category', 'category_display', 
            'status', 'status_display', 'business', 'business_name',
            'messages_count', 'last_message', 'last_message_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'title', 'category_display', 'status_display',
            'messages_count', 'last_message', 'last_message_at',
            'created_at', 'updated_at'
        ]
    
    def get_last_message(self, obj):
        """Возвращает последнее сообщение в диалоге"""
        last_msg = obj.get_last_message()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100] + ('...' if len(last_msg.content) > 100 else ''),
                'created_at': last_msg.created_at
            }
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer для создания нового диалога
    """
    first_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text='Первое сообщение в диалоге'
    )
    
    class Meta:
        model = Conversation
        fields = ['category', 'business', 'first_message']
        extra_kwargs = {
            'category': {'required': False},
            'business': {'required': False},
        }
    
    def validate_business(self, value):
        """Проверка, что бизнес принадлежит текущему пользователю"""
        if value:
            user = self.context['request'].user
            if value.owner != user:
                raise serializers.ValidationError(
                    "Вы не можете создать диалог для чужого бизнеса"
                )
        return value
    
    def create(self, validated_data):
        """Создание диалога с первым сообщением"""
        first_message_content = validated_data.pop('first_message', None)
        user = self.context['request'].user
        
        # Создаем диалог
        conversation = Conversation.objects.create(
            user=user,
            **validated_data
        )
        
        # Если передано первое сообщение, создаем его
        if first_message_content:
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content=first_message_content
            )
        
        return conversation


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Детальный serializer для диалога с сообщениями
    """
    messages = MessageSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    business_detail = BusinessSerializer(source='business', read_only=True)
    messages_count = serializers.IntegerField(source='get_messages_count', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'category', 'category_display',
            'status', 'status_display', 'business', 'business_detail',
            'messages_count', 'messages', 'last_message_at',
            'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = [
            'id', 'title', 'category_display', 'status_display',
            'messages_count', 'messages', 'last_message_at',
            'created_at', 'updated_at'
        ]


class ConversationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer для обновления диалога
    """
    
    class Meta:
        model = Conversation
        fields = ['title', 'category', 'status']

