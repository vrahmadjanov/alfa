"""
Unit тесты для LLM сервиса и интеграции с OpenRouter
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, override_settings
from django.conf import settings

from users.models import User
from chat.models import Conversation, Message
from chat.services import LLMService


class LLMServiceInitTest(TestCase):
    """
    Тесты инициализации LLMService
    """
    
    def test_service_initialization(self):
        """Тест правильной инициализации сервиса"""
        service = LLMService()
        
        self.assertIsNotNone(service.client)
        self.assertEqual(service.models, settings.OPENROUTER_MODELS)
        self.assertEqual(service.primary_model, settings.OPENROUTER_MODEL)
        self.assertEqual(service.site_url, settings.OPENROUTER_SITE_URL)
        self.assertEqual(service.site_name, settings.OPENROUTER_SITE_NAME)
    
    def test_models_list_not_empty(self):
        """Тест что список моделей не пустой"""
        service = LLMService()
        
        self.assertGreater(len(service.models), 0)
        self.assertIn(service.primary_model, service.models + [settings.OPENROUTER_MODEL])


class LLMServiceGenerateResponseTest(TestCase):
    """
    Тесты генерации ответов с мокированием API
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            category='marketing'
        )
        self.user_message = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Помоги с маркетингом'
        )
        self.service = LLMService()
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_successful_response_first_model(self, mock_build_history):
        """Тест успешного ответа с первой модели"""
        mock_build_history.return_value = [
            {'role': 'system', 'content': 'Test system prompt'},
            {'role': 'user', 'content': 'Помоги с маркетингом'}
        ]
        
        # Mock успешного ответа от API
        mock_completion = Mock()
        mock_completion.choices = [Mock(
            message=Mock(content='Отличный вопрос о маркетинге!'),
            finish_reason='stop'
        )]
        mock_completion.model = 'qwen-30b'
        mock_completion.usage = Mock(total_tokens=150)
        
        self.service.client.chat.completions.create = Mock(return_value=mock_completion)
        
        result = self.service.generate_response(
            conversation=self.conversation,
            user_message=self.user_message
        )
        
        # Проверяем результат
        self.assertEqual(result['content'], 'Отличный вопрос о маркетинге!')
        self.assertEqual(result['model'], 'qwen-30b')
        self.assertEqual(result['tokens_used'], 150)
        self.assertIsNotNone(result['response_time'])
        self.assertIn('metadata', result)
        self.assertEqual(result['metadata']['attempted_models'], 1)
        self.assertFalse(result['metadata']['fallback_used'])
        
        # Проверяем, что API был вызван один раз
        self.assertEqual(self.service.client.chat.completions.create.call_count, 1)
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_fallback_to_second_model(self, mock_build_history):
        """Тест fallback на вторую модель при rate limit первой"""
        from openai import RateLimitError
        
        mock_build_history.return_value = [
            {'role': 'user', 'content': 'Test'}
        ]
        
        # Mock успешного ответа от второй модели
        mock_completion = Mock()
        mock_completion.choices = [Mock(
            message=Mock(content='Ответ от второй модели'),
            finish_reason='stop'
        )]
        mock_completion.model = 'qwen-14b'
        mock_completion.usage = Mock(total_tokens=100)
        
        # Создаем правильную RateLimitError с mock response
        mock_response = Mock()
        mock_response.status_code = 429
        rate_limit_error = RateLimitError(
            'Rate limit exceeded',
            response=mock_response,
            body={'error': 'rate limit'}
        )
        
        # Первый вызов - RateLimitError, второй - успех
        self.service.client.chat.completions.create = Mock(
            side_effect=[
                rate_limit_error,
                mock_completion
            ]
        )
        
        result = self.service.generate_response(
            conversation=self.conversation,
            user_message=self.user_message
        )
        
        # Проверяем успешный fallback
        self.assertEqual(result['content'], 'Ответ от второй модели')
        self.assertEqual(result['model'], 'qwen-14b')
        self.assertEqual(result['metadata']['attempted_models'], 2)
        self.assertTrue(result['metadata']['fallback_used'])
        
        # Проверяем, что было 2 попытки
        self.assertEqual(self.service.client.chat.completions.create.call_count, 2)
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_fallback_through_multiple_models(self, mock_build_history):
        """Тест fallback через несколько моделей"""
        from openai import RateLimitError, APITimeoutError
        
        mock_build_history.return_value = [{'role': 'user', 'content': 'Test'}]
        
        # Mock успешного ответа от третьей модели
        mock_completion = Mock()
        mock_completion.choices = [Mock(
            message=Mock(content='Ответ от третьей модели'),
            finish_reason='stop'
        )]
        mock_completion.model = 'qwen-235b'
        mock_completion.usage = Mock(total_tokens=200)
        
        # Создаем правильные ошибки
        mock_response = Mock()
        mock_response.status_code = 429
        rate_limit_error = RateLimitError(
            'Rate limit',
            response=mock_response,
            body={'error': 'rate limit'}
        )
        
        mock_request = Mock()
        timeout_error = APITimeoutError(request=mock_request)
        
        # Первые две попытки - ошибки, третья - успех
        self.service.client.chat.completions.create = Mock(
            side_effect=[
                rate_limit_error,
                timeout_error,
                mock_completion
            ]
        )
        
        result = self.service.generate_response(
            conversation=self.conversation,
            user_message=self.user_message
        )
        
        # Проверяем успешный fallback на третью модель
        self.assertEqual(result['content'], 'Ответ от третьей модели')
        self.assertEqual(result['metadata']['attempted_models'], 3)
        self.assertTrue(result['metadata']['fallback_used'])
        
        # Проверяем количество попыток
        self.assertEqual(self.service.client.chat.completions.create.call_count, 3)
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_all_models_fail(self, mock_build_history):
        """Тест когда все модели не работают"""
        from openai import RateLimitError
        
        mock_build_history.return_value = [{'role': 'user', 'content': 'Test'}]
        
        # Создаем правильную RateLimitError
        mock_response = Mock()
        mock_response.status_code = 429
        rate_limit_error = RateLimitError(
            'Rate limit exceeded',
            response=mock_response,
            body={'error': 'rate limit'}
        )
        
        # Все попытки возвращают ошибку
        self.service.client.chat.completions.create = Mock(
            side_effect=rate_limit_error
        )
        
        result = self.service.generate_response(
            conversation=self.conversation,
            user_message=self.user_message
        )
        
        # Проверяем fallback сообщение
        self.assertEqual(result['model'], 'error-fallback')
        self.assertIn('слишком много запросов', result['content'])
        self.assertIn('metadata', result)
        self.assertTrue(result['metadata']['error'])
        self.assertEqual(result['metadata']['error_type'], 'rate_limit')
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_api_error_404_stops_fallback(self, mock_build_history):
        """Тест что 404 ошибка останавливает fallback"""
        from openai import APIStatusError
        
        mock_build_history.return_value = [{'role': 'user', 'content': 'Test'}]
        
        # Создаем правильную APIStatusError с 404
        mock_response = Mock()
        mock_response.status_code = 404
        api_error = APIStatusError(
            'Not found',
            response=mock_response,
            body={'error': 'not found'}
        )
        api_error.status_code = 404
        
        self.service.client.chat.completions.create = Mock(side_effect=api_error)
        
        result = self.service.generate_response(
            conversation=self.conversation,
            user_message=self.user_message
        )
        
        # Проверяем, что вернулась ошибка без долгих попыток
        self.assertEqual(result['model'], 'error-fallback')
        self.assertEqual(result['metadata']['error_type'], 'api_error')
        
        # Проверяем, что была только одна попытка (404 останавливает fallback)
        self.assertEqual(self.service.client.chat.completions.create.call_count, 1)
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_response_without_usage_info(self, mock_build_history):
        """Тест обработки ответа без информации о токенах"""
        mock_build_history.return_value = [{'role': 'user', 'content': 'Test'}]
        
        # Mock ответа без usage
        mock_completion = Mock(spec=['choices', 'model'])
        mock_completion.choices = [Mock(
            message=Mock(content='Ответ без токенов'),
            finish_reason='stop'
        )]
        mock_completion.model = 'test-model'
        # Явно не добавляем атрибут usage - используем spec
        
        self.service.client.chat.completions.create = Mock(return_value=mock_completion)
        
        result = self.service.generate_response(
            conversation=self.conversation,
            user_message=self.user_message
        )
        
        # Проверяем, что токены None
        self.assertIsNone(result['tokens_used'])
        self.assertEqual(result['content'], 'Ответ без токенов')


class LLMServiceCreateMessageTest(TestCase):
    """
    Тесты создания сообщения ассистента
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            category='general'
        )
    
    def test_create_assistant_message(self):
        """Тест создания сообщения ассистента"""
        response_data = {
            'content': 'Привет! Чем могу помочь?',
            'model': 'qwen-30b',
            'tokens_used': 50,
            'response_time': 2.5,
            'metadata': {
                'temperature': 0.7,
                'attempted_models': 1,
                'fallback_used': False
            }
        }
        
        message = LLMService.create_assistant_message(
            conversation=self.conversation,
            response_data=response_data
        )
        
        # Проверяем созданное сообщение
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.role, Message.Role.ASSISTANT)
        self.assertEqual(message.content, 'Привет! Чем могу помочь?')
        self.assertEqual(message.model, 'qwen-30b')
        self.assertEqual(message.tokens_used, 50)
        self.assertEqual(message.response_time, 2.5)
        self.assertIsNotNone(message.metadata)
        self.assertFalse(message.metadata['fallback_used'])
    
    def test_create_message_updates_conversation(self):
        """Тест что создание сообщения обновляет диалог"""
        self.assertIsNone(self.conversation.last_message_at)
        
        response_data = {
            'content': 'Test',
            'model': 'test-model',
            'tokens_used': 10,
            'response_time': 1.0,
            'metadata': {}
        }
        
        message = LLMService.create_assistant_message(
            conversation=self.conversation,
            response_data=response_data
        )
        
        # Проверяем обновление диалога
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.last_message_at)
        self.assertEqual(self.conversation.last_message_at, message.created_at)


class LLMServiceErrorHandlingTest(TestCase):
    """
    Тесты обработки различных типов ошибок
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.service = LLMService()
    
    def test_handle_rate_limit_error(self):
        """Тест обработки rate limit ошибки"""
        error = Exception('Rate limit exceeded')
        
        result = self.service._handle_error('rate_limit', error, 2.5)
        
        self.assertEqual(result['model'], 'error-fallback')
        self.assertIn('слишком много запросов', result['content'])
        self.assertEqual(result['response_time'], 2.5)
        self.assertTrue(result['metadata']['error'])
        self.assertEqual(result['metadata']['error_type'], 'rate_limit')
    
    def test_handle_timeout_error(self):
        """Тест обработки timeout ошибки"""
        error = Exception('Timeout')
        
        result = self.service._handle_error('timeout', error, 30.0)
        
        self.assertEqual(result['model'], 'error-fallback')
        self.assertIn('слишком много времени', result['content'])
        self.assertEqual(result['response_time'], 30.0)
        self.assertEqual(result['metadata']['error_type'], 'timeout')
    
    def test_handle_api_error(self):
        """Тест обработки API ошибки"""
        error = Exception('API Error')
        
        result = self.service._handle_error('api_error', error, 1.5)
        
        self.assertEqual(result['model'], 'error-fallback')
        self.assertIn('произошла техническая ошибка', result['content'])
        self.assertEqual(result['metadata']['error_type'], 'api_error')
    
    def test_handle_default_error(self):
        """Тест обработки неизвестной ошибки"""
        error = Exception('Unknown error')
        
        result = self.service._handle_error('default', error, 0.5)
        
        self.assertEqual(result['model'], 'error-fallback')
        self.assertIn('не удалось получить ответ', result['content'])
        self.assertEqual(result['metadata']['error_type'], 'default')


@override_settings(
    OPENROUTER_MODELS=['model1', 'model2', 'model3'],
    OPENROUTER_MODEL='model1'
)
class LLMServiceConfigurationTest(TestCase):
    """
    Тесты конфигурации моделей
    """
    
    def test_uses_custom_models_list(self):
        """Тест использования кастомного списка моделей"""
        service = LLMService()
        
        self.assertEqual(service.models, ['model1', 'model2', 'model3'])
        self.assertEqual(service.primary_model, 'model1')
    
    @patch('chat.services.llm_service.PromptBuilder.build_messages_history')
    def test_tries_all_custom_models(self, mock_build_history):
        """Тест что пробуются все модели из кастомного списка"""
        from openai import RateLimitError
        
        mock_build_history.return_value = [{'role': 'user', 'content': 'Test'}]
        
        service = LLMService()
        
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        conversation = Conversation.objects.create(user=user, category='general')
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Test'
        )
        
        # Создаем правильную RateLimitError
        mock_response = Mock()
        mock_response.status_code = 429
        rate_limit_error = RateLimitError(
            'Rate limit',
            response=mock_response,
            body={'error': 'rate limit'}
        )
        
        # Все модели возвращают ошибку
        service.client.chat.completions.create = Mock(
            side_effect=rate_limit_error
        )
        
        result = service.generate_response(
            conversation=conversation,
            user_message=message
        )
        
        # Проверяем, что было попробовано 3 модели
        self.assertEqual(service.client.chat.completions.create.call_count, 3)
        self.assertEqual(result['model'], 'error-fallback')

