"""
Views для Chat API
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from chat.models import Conversation, Message
from chat.serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    ConversationDetailSerializer,
    ConversationUpdateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from chat.services import LLMService
from users.utils.api_response import APIResponse, format_serializer_errors


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    API endpoint для списка диалогов и создания нового
    
    GET /api/chat/conversations/
    POST /api/chat/conversations/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращаем только диалоги текущего пользователя"""
        return Conversation.objects.filter(
            user=self.request.user
        ).select_related('business', 'user').prefetch_related('messages')
    
    def get_serializer_class(self):
        """Используем разные serializers для GET и POST"""
        if self.request.method == 'POST':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def list(self, request, *args, **kwargs):
        """GET - список всех диалогов"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Фильтрация по статусу
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтрация по категории
        category_filter = request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        # Фильтрация по бизнесу
        business_id = request.query_params.get('business')
        if business_id:
            queryset = queryset.filter(business_id=business_id)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=f"Найдено диалогов: {len(serializer.data)}"
        )
    
    def create(self, request, *args, **kwargs):
        """POST - создание нового диалога"""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        conversation = serializer.save()
        
        # Возвращаем детальную информацию о созданном диалоге
        detail_serializer = ConversationDetailSerializer(conversation)
        
        return APIResponse.created(
            data=detail_serializer.data,
            message="Диалог успешно создан"
        )


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для работы с конкретным диалогом
    
    GET /api/chat/conversations/{id}/
    PATCH /api/chat/conversations/{id}/
    DELETE /api/chat/conversations/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращаем только диалоги текущего пользователя"""
        return Conversation.objects.filter(
            user=self.request.user
        ).select_related('business', 'user').prefetch_related('messages')
    
    def get_serializer_class(self):
        """Используем разные serializers для разных методов"""
        if self.request.method in ['PUT', 'PATCH']:
            return ConversationUpdateSerializer
        return ConversationDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """GET - получение детальной информации о диалоге"""
        instance = self.get_object()
        serializer = ConversationDetailSerializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message="Информация о диалоге получена"
        )
    
    def update(self, request, *args, **kwargs):
        """PATCH/PUT - обновление диалога"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        self.perform_update(serializer)
        
        # Возвращаем детальную информацию
        detail_serializer = ConversationDetailSerializer(instance)
        
        return APIResponse.success(
            data=detail_serializer.data,
            message="Диалог успешно обновлен"
        )
    
    def destroy(self, request, *args, **kwargs):
        """DELETE - архивирование диалога"""
        instance = self.get_object()
        
        # Вместо удаления - архивируем
        instance.status = Conversation.Status.ARCHIVED
        instance.save()
        
        return APIResponse.success(
            message="Диалог успешно архивирован"
        )


class MessageCreateView(APIView):
    """
    API endpoint для работы с сообщениями в диалоге
    
    GET /api/chat/conversations/{conversation_id}/messages/ - список сообщений
    POST /api/chat/conversations/{conversation_id}/messages/ - отправить сообщение
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, conversation_id):
        """GET - получить список сообщений"""
        # Проверяем, что диалог принадлежит пользователю
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        
        # Получаем все сообщения
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=f"Найдено сообщений: {len(serializer.data)}"
        )
    
    def post(self, request, conversation_id):
        """POST - отправить сообщение и получить ответ от AI"""
        # Проверяем, что диалог принадлежит пользователю
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        
        # Валидация сообщения
        serializer = MessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации сообщения"
            )
        
        # Создаем сообщение пользователя
        user_message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=serializer.validated_data['content']
        )
        
        # Генерируем ответ от LLM
        llm_service = LLMService()
        response_data = llm_service.generate_response(
            conversation=conversation,
            user_message=user_message
        )
        
        # Создаем сообщение ассистента
        assistant_message = LLMService.create_assistant_message(
            conversation=conversation,
            response_data=response_data
        )
        
        # Возвращаем оба сообщения
        return APIResponse.success(
            data={
                'user_message': MessageSerializer(user_message).data,
                'assistant_message': MessageSerializer(assistant_message).data
            },
            message="Сообщение отправлено"
        )


class ConversationStatsView(APIView):
    """
    API endpoint для получения статистики по диалогам пользователя
    
    GET /api/chat/stats/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение статистики по диалогам"""
        user = request.user
        
        conversations = Conversation.objects.filter(user=user)
        
        stats = {
            'total_conversations': conversations.count(),
            'active_conversations': conversations.filter(status=Conversation.Status.ACTIVE).count(),
            'archived_conversations': conversations.filter(status=Conversation.Status.ARCHIVED).count(),
            'total_messages': Message.objects.filter(conversation__user=user).count(),
            'by_category': {}
        }
        
        # Статистика по категориям
        for category in Conversation.Category:
            count = conversations.filter(category=category.value).count()
            if count > 0:
                stats['by_category'][category.value] = {
                    'name': category.label,
                    'count': count
                }
        
        return APIResponse.success(
            data=stats,
            message="Статистика получена"
        )
