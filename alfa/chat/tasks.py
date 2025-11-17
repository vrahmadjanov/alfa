"""
Celery задачи для асинхронной обработки сообщений
"""
import logging
from celery import shared_task
from django.utils import timezone

from chat.models import Message
from chat.services import LLMService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_ai_response(self, message_id):
    """
    Асинхронная генерация ответа от AI для сообщения пользователя
    
    Args:
        message_id: ID сообщения пользователя
    
    Returns:
        ID созданного сообщения ассистента
    """
    try:
        # Получаем сообщение пользователя
        user_message = Message.objects.select_related('conversation').get(id=message_id)
        
        # Обновляем статус на "обрабатывается"
        user_message.processing_status = Message.ProcessingStatus.PROCESSING
        user_message.save(update_fields=['processing_status'])
        
        logger.info(f'Starting AI response generation for message {message_id}')
        
        # Генерируем ответ
        llm_service = LLMService()
        response_data = llm_service.generate_response(
            conversation=user_message.conversation,
            user_message=user_message
        )
        
        # Создаем сообщение ассистента
        assistant_message = LLMService.create_assistant_message(
            conversation=user_message.conversation,
            response_data=response_data
        )
        
        # Обновляем статус на "завершено"
        user_message.processing_status = Message.ProcessingStatus.COMPLETED
        user_message.save(update_fields=['processing_status'])
        
        logger.info(f'AI response generated successfully for message {message_id}')
        
        return assistant_message.id
        
    except Message.DoesNotExist:
        logger.error(f'Message {message_id} not found')
        raise
        
    except Exception as exc:
        logger.error(f'Error generating AI response for message {message_id}: {exc}')
        
        # Обновляем статус на "ошибка"
        try:
            user_message = Message.objects.get(id=message_id)
            user_message.processing_status = Message.ProcessingStatus.FAILED
            user_message.save(update_fields=['processing_status'])
        except:
            pass
        
        # Повторяем попытку с экспоненциальной задержкой
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

