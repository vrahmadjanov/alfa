"""
Views для Chat API
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models

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
        if 'business' in request.query_params:
            business_id = request.query_params.get('business')
            if business_id:
                queryset = queryset.filter(business_id=business_id)
            else:
                # Если передан параметр business, но он пустой, показываем только диалоги без бизнеса
                queryset = queryset.filter(business__isnull=True)
        
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
        """POST - отправить сообщение и запустить асинхронную генерацию ответа от AI"""
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
        
        # Создаем сообщение пользователя с статусом "ожидает обработки"
        user_message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=serializer.validated_data['content'],
            processing_status=Message.ProcessingStatus.PENDING
        )
        
        # Запускаем асинхронную задачу для генерации ответа
        from chat.tasks import generate_ai_response
        task = generate_ai_response.delay(user_message.id)
        
        # Возвращаем сообщение пользователя и ID задачи
        return APIResponse.success(
            data={
                'user_message': MessageSerializer(user_message).data,
                'task_id': task.id
            },
            message="Сообщение отправлено, генерация ответа начата"
        )


class MessageStatusView(APIView):
    """
    API endpoint для проверки статуса обработки сообщения
    
    GET /api/chat/conversations/{conversation_id}/messages/{message_id}/status/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, conversation_id, message_id):
        """Получение статуса обработки сообщения"""
        # Проверяем, что сообщение существует и принадлежит пользователю
        message = get_object_or_404(
            Message,
            id=message_id,
            conversation_id=conversation_id,
            conversation__user=request.user
        )
        
        # Если сообщение обработано, получаем ответ ассистента
        assistant_message = None
        if message.processing_status == Message.ProcessingStatus.COMPLETED:
            # Ищем следующее сообщение ассистента
            assistant_message = Message.objects.filter(
                conversation_id=conversation_id,
                role=Message.Role.ASSISTANT,
                created_at__gt=message.created_at
            ).order_by('created_at').first()
        
        data = {
            'message_id': message.id,
            'processing_status': message.processing_status,
            'processing_status_display': message.get_processing_status_display(),
        }
        
        if assistant_message:
            data['assistant_message'] = MessageSerializer(assistant_message).data
        
        return APIResponse.success(
            data=data,
            message="Статус получен"
        )


class ConversationStatsView(APIView):
    """
    API endpoint для получения статистики по диалогам пользователя
    
    GET /api/chat/stats/ - общая статистика
    GET /api/chat/stats/?business=<id> - статистика по конкретному бизнесу
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение статистики по диалогам"""
        user = request.user
        business_id = request.query_params.get('business')
        
        # Базовый queryset
        conversations = Conversation.objects.filter(user=user)
        messages_query = Message.objects.filter(conversation__user=user)
        
        # Фильтрация по бизнесу, если указан
        if business_id:
            conversations = conversations.filter(business_id=business_id)
            messages_query = messages_query.filter(conversation__business_id=business_id)
        
        # Последний диалог для определения последней активности
        last_conversation = conversations.order_by('-last_message_at').first()
        
        stats = {
            'total_conversations': conversations.count(),
            'active_conversations': conversations.filter(status=Conversation.Status.ACTIVE).count(),
            'archived_conversations': conversations.filter(status=Conversation.Status.ARCHIVED).count(),
            'completed_conversations': conversations.filter(status=Conversation.Status.COMPLETED).count(),
            'total_messages': messages_query.count(),
            'user_messages': messages_query.filter(role=Message.Role.USER).count(),
            'assistant_messages': messages_query.filter(role=Message.Role.ASSISTANT).count(),
            'total_tokens_used': messages_query.aggregate(
                total=models.Sum('tokens_used')
            )['total'] or 0,
            'last_activity': last_conversation.last_message_at if last_conversation else None,
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
        
        # Если запрашивается статистика по бизнесу, добавляем информацию о бизнесе
        if business_id:
            from users.models import Business
            business = Business.objects.filter(id=business_id, owner=user).first()
            if business:
                stats['business'] = {
                    'id': business.id,
                    'name': business.name
                }
        
        return APIResponse.success(
            data=stats,
            message="Статистика получена"
        )
