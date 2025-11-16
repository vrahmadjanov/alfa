"""
Сервис для работы с LLM через OpenRouter API
"""
import time
import logging
from typing import Dict, Optional
from django.conf import settings
from openai import OpenAI, APIError, RateLimitError, APITimeoutError

from chat.models import Conversation, Message
from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class LLMService:
    """
    Сервис для взаимодействия с LLM через OpenRouter
    Поддерживает автоматическое переключение между моделями при ошибках
    """
    
    def __init__(self):
        """Инициализация клиента OpenAI с OpenRouter"""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.models = settings.OPENROUTER_MODELS
        self.primary_model = settings.OPENROUTER_MODEL
        self.site_url = settings.OPENROUTER_SITE_URL
        self.site_name = settings.OPENROUTER_SITE_NAME
    
    def generate_response(
        self,
        conversation: Conversation,
        user_message: Message,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, any]:
        """
        Генерирует ответ от LLM с автоматическим fallback на другие модели
        
        Args:
            conversation: Диалог
            user_message: Сообщение пользователя
            temperature: Параметр креативности (0.0-1.0)
            max_tokens: Максимальное количество токенов в ответе
        
        Returns:
            Dict с содержимым ответа и метаданными:
            {
                'content': str,  # Текст ответа
                'model': str,    # Модель которая использовалась
                'tokens_used': int,  # Количество токенов
                'response_time': float,  # Время генерации в секундах
                'metadata': dict  # Дополнительные данные
            }
        """
        start_time = time.time()
        
        # Строим историю сообщений с контекстом
        messages = PromptBuilder.build_messages_history(conversation)
        
        # Пробуем основную модель, затем fallback модели
        models_to_try = [self.primary_model] + [m for m in self.models if m != self.primary_model]
        
        last_error = None
        for model_index, model in enumerate(models_to_try):
            try:
                # Логируем попытку
                if model_index == 0:
                    logger.info(f"Попытка генерации с моделью {model} для диалога {conversation.id}")
                else:
                    logger.warning(f"Fallback на модель {model} для диалога {conversation.id}")
                
                # Делаем запрос к OpenRouter
                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                response_time = time.time() - start_time
                
                # Извлекаем данные из ответа
                content = completion.choices[0].message.content
                model_used = completion.model
                
                # Подсчет токенов
                tokens_used = None
                if hasattr(completion, 'usage'):
                    tokens_used = completion.usage.total_tokens
                
                result = {
                    'content': content,
                    'model': model_used,
                    'tokens_used': tokens_used,
                    'response_time': round(response_time, 2),
                    'metadata': {
                        'temperature': temperature,
                        'max_tokens': max_tokens,
                        'finish_reason': completion.choices[0].finish_reason if completion.choices else None,
                        'attempted_models': model_index + 1,
                        'fallback_used': model_index > 0
                    }
                }
                
                logger.info(
                    f"✓ Успешно сгенерирован ответ для диалога {conversation.id}. "
                    f"Модель: {model_used}, Токены: {tokens_used}, "
                    f"Время: {response_time:.2f}с, Попыток: {model_index + 1}"
                )
                
                return result
                
            except RateLimitError as e:
                last_error = ('rate_limit', e)
                logger.warning(f"✗ Rate limit для модели {model}: {str(e)}")
                continue
            
            except APITimeoutError as e:
                last_error = ('timeout', e)
                logger.warning(f"✗ Timeout для модели {model}: {str(e)}")
                continue
            
            except APIError as e:
                last_error = ('api_error', e)
                logger.warning(f"✗ API ошибка для модели {model}: {str(e)}")
                # Для 404 ошибок не пробуем другие модели, сразу возвращаем ошибку
                if hasattr(e, 'status_code') and e.status_code == 404:
                    break
                continue
            
            except Exception as e:
                last_error = ('default', e)
                logger.warning(f"✗ Ошибка для модели {model}: {str(e)}")
                continue
        
        # Все модели не сработали - возвращаем ошибку
        response_time = time.time() - start_time
        error_type, error = last_error if last_error else ('default', Exception('Unknown error'))
        
        logger.error(
            f"✗✗✗ Все модели ({len(models_to_try)}) не смогли сгенерировать ответ "
            f"для диалога {conversation.id}. Последняя ошибка: {error_type}"
        )
        
        return self._handle_error(error_type, error, response_time)
    
    def _handle_error(self, error_type: str, error: Exception, response_time: float) -> Dict[str, any]:
        """
        Обработка ошибок при генерации ответа
        
        Args:
            error_type: Тип ошибки
            error: Исключение
            response_time: Время до ошибки
        
        Returns:
            Dict с fallback ответом
        """
        content = PromptBuilder.format_error_response(error_type)
        
        return {
            'content': content,
            'model': 'error-fallback',
            'tokens_used': None,
            'response_time': round(response_time, 2),
            'metadata': {
                'error': True,
                'error_type': error_type,
                'error_message': str(error)
            }
        }
    
    @staticmethod
    def create_assistant_message(
        conversation: Conversation,
        response_data: Dict[str, any]
    ) -> Message:
        """
        Создает сообщение ассистента на основе ответа LLM
        
        Args:
            conversation: Диалог
            response_data: Данные ответа от generate_response
        
        Returns:
            Созданное сообщение Message
        """
        message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=response_data['content'],
            model=response_data['model'],
            tokens_used=response_data['tokens_used'],
            response_time=response_data['response_time'],
            metadata=response_data['metadata']
        )
        
        return message

