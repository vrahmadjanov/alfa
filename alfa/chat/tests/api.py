"""
API тесты для чата с AI ассистентом
"""
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Business
from chat.models import Conversation, Message


class ConversationCreateAPITest(APITestCase):
    """
    Тесты для создания диалога
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        
        self.business = Business.objects.create(
            owner=self.user,
            name='Тестовая Кофейня',
            business_type='cafe'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.create_url = reverse('chat:conversation_list_create')
    
    def test_create_conversation_success(self):
        """Тест успешного создания диалога"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'category': 'marketing',
            'business': self.business.id
        }
        
        response = self.client.post(self.create_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['category'], 'marketing')
        
        # Проверяем, что диалог создан в БД
        self.assertTrue(Conversation.objects.filter(user=self.user).exists())
        
        # Проверяем, что диалог создан без сообщений
        conversation = Conversation.objects.get(user=self.user)
        self.assertEqual(conversation.messages.count(), 0)
    
    def test_create_conversation_without_business(self):
        """Тест создания диалога без привязки к бизнесу"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'category': 'general'
        }
        
        response = self.client.post(self.create_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIsNone(response.data['data']['business'])
    
    def test_create_conversation_without_auth(self):
        """Тест создания без аутентификации"""
        response = self.client.post(self.create_url, data={}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_conversation_with_other_user_business(self):
        """Тест попытки создать диалог с чужим бизнесом"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )
        other_business = Business.objects.create(
            owner=other_user,
            name='Чужой бизнес',
            business_type='cafe'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'business': other_business.id
        }
        
        response = self.client.post(self.create_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class ConversationListAPITest(APITestCase):
    """
    Тесты для получения списка диалогов
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPassword123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPassword123!'
        )
        
        self.business1 = Business.objects.create(
            owner=self.user1,
            name='Бизнес 1',
            business_type='cafe'
        )
        
        # Создаем диалоги для user1
        self.conv1 = Conversation.objects.create(
            user=self.user1,
            business=self.business1,
            title='Диалог о маркетинге',
            category='marketing',
            status='active'
        )
        self.conv2 = Conversation.objects.create(
            user=self.user1,
            title='Юридический вопрос',
            category='legal',
            status='active'
        )
        self.conv3 = Conversation.objects.create(
            user=self.user1,
            title='Архивный диалог',
            category='general',
            status='archived'
        )
        
        # Создаем диалог для user2
        Conversation.objects.create(
            user=self.user2,
            title='Чужой диалог',
            category='general'
        )
        
        self.refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(self.refresh.access_token)
        
        self.list_url = reverse('chat:conversation_list_create')
    
    def test_list_conversations_success(self):
        """Тест получения списка своих диалогов"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)  # Только диалоги user1
    
    def test_list_conversations_filter_by_status(self):
        """Тест фильтрации по статусу"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(f'{self.list_url}?status=active')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)  # Только активные
    
    def test_list_conversations_filter_by_category(self):
        """Тест фильтрации по категории"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(f'{self.list_url}?category=marketing')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['category'], 'marketing')
    
    def test_list_conversations_filter_by_business(self):
        """Тест фильтрации по бизнесу"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(f'{self.list_url}?business={self.business1.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['business'], self.business1.id)
    
    def test_list_conversations_filter_by_no_business(self):
        """Тест фильтрации диалогов без привязки к бизнесу"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Передаем пустой параметр business для получения только диалогов без бизнеса
        response = self.client.get(f'{self.list_url}?business=')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)  # conv2 и conv3 без бизнеса
        
        # Проверяем, что все диалоги без бизнеса
        for conversation in response.data['data']:
            self.assertIsNone(conversation['business'])


class ConversationDetailAPITest(APITestCase):
    """
    Тесты для работы с конкретным диалогом
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Тестовый диалог',
            category='marketing'
        )
        
        # Добавляем сообщения
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Привет!'
        )
        Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content='Здравствуйте!',
            model='test-model'
        )
        
        self.other_conversation = Conversation.objects.create(
            user=self.other_user,
            title='Чужой диалог',
            category='general'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.detail_url = reverse('chat:conversation_detail', kwargs={'pk': self.conversation.id})
        self.other_detail_url = reverse('chat:conversation_detail', kwargs={'pk': self.other_conversation.id})
    
    def test_get_conversation_detail_success(self):
        """Тест получения детальной информации о диалоге"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['title'], self.conversation.title)
        self.assertIn('messages', response.data['data'])
        self.assertEqual(len(response.data['data']['messages']), 2)
    
    def test_get_other_user_conversation(self):
        """Тест попытки получить чужой диалог"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.other_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_conversation_success(self):
        """Тест обновления диалога"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        update_data = {
            'title': 'Новый заголовок',
            'category': 'finance'
        }
        
        response = self.client.patch(self.detail_url, data=update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['title'], 'Новый заголовок')
        
        # Проверяем обновление в БД
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'Новый заголовок')
    
    def test_delete_conversation_archives(self):
        """Тест архивирования диалога при удалении"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Проверяем, что диалог архивирован, а не удален
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.status, Conversation.Status.ARCHIVED)


class MessageAPITest(APITestCase):
    """
    Тесты для работы с сообщениями
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Тестовый диалог',
            category='marketing'
        )
        
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Первое сообщение'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.messages_url = reverse('chat:messages', kwargs={'conversation_id': self.conversation.id})
    
    @patch('chat.views.LLMService')
    def test_send_message_success(self, MockLLMService):
        """Тест успешной отправки сообщения"""
        # Настраиваем mock для экземпляра LLMService
        mock_instance = MockLLMService.return_value
        
        # Mock generate_response - метод экземпляра
        mock_response_data = {
            'content': 'Привет! Я помогу вам с маркетингом.',
            'model': 'test-model',
            'tokens_used': 50,
            'response_time': 1.5,
            'metadata': {}
        }
        mock_instance.generate_response.return_value = mock_response_data
        
        # Mock create_assistant_message - статический метод класса
        # Реально создаем сообщение в БД, чтобы тест был корректным
        MockLLMService.create_assistant_message = lambda conversation, response_data: Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=response_data['content'],
            model=response_data['model'],
            tokens_used=response_data['tokens_used'],
            response_time=response_data['response_time']
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'content': 'Нужна помощь с маркетингом'
        }
        
        response = self.client.post(self.messages_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('user_message', response.data['data'])
        self.assertIn('assistant_message', response.data['data'])
        
        # Проверяем, что сообщения созданы в БД
        self.assertEqual(self.conversation.messages.count(), 3)  # 1 начальное + 2 новых
        
        # Проверяем, что LLM был вызван
        mock_instance.generate_response.assert_called_once()
    
    def test_send_empty_message(self):
        """Тест отправки пустого сообщения"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'content': '   '
        }
        
        response = self.client.post(self.messages_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_send_too_long_message(self):
        """Тест отправки слишком длинного сообщения"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'content': 'a' * 4001
        }
        
        response = self.client.post(self.messages_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_list_messages_success(self):
        """Тест получения списка сообщений"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.messages_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)


class ConversationStatsAPITest(APITestCase):
    """
    Тесты для получения статистики по диалогам
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        
        # Создаем бизнес
        self.business = Business.objects.create(
            owner=self.user,
            name='Тестовый бизнес',
            business_type='cafe'
        )
        
        # Создаем диалоги разных категорий (2 с бизнесом, 2 без)
        Conversation.objects.create(
            user=self.user,
            business=self.business,
            title='Маркетинг 1',
            category='marketing',
            status='active'
        )
        Conversation.objects.create(
            user=self.user,
            business=self.business,
            title='Маркетинг 2',
            category='marketing',
            status='active'
        )
        Conversation.objects.create(
            user=self.user,
            title='Юридический',
            category='legal',
            status='active'
        )
        archived_conv = Conversation.objects.create(
            user=self.user,
            title='Архивный',
            category='general',
            status='archived'
        )
        
        # Добавляем сообщения
        Message.objects.create(
            conversation=archived_conv,
            role='user',
            content='Test'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.stats_url = reverse('chat:stats')
    
    def test_get_stats_success(self):
        """Тест получения общей статистики"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        stats = response.data['data']
        self.assertEqual(stats['total_conversations'], 4)
        self.assertEqual(stats['active_conversations'], 3)
        self.assertEqual(stats['archived_conversations'], 1)
        self.assertEqual(stats['total_messages'], 1)
        self.assertIn('by_category', stats)
        self.assertIn('total_tokens_used', stats)
        self.assertIn('user_messages', stats)
        self.assertIn('assistant_messages', stats)
    
    def test_get_stats_by_business(self):
        """Тест получения статистики по конкретному бизнесу"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(f'{self.stats_url}?business={self.business.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        stats = response.data['data']
        # Только 2 диалога связаны с бизнесом
        self.assertEqual(stats['total_conversations'], 2)
        self.assertIn('business', stats)
        self.assertEqual(stats['business']['id'], self.business.id)
        self.assertEqual(stats['business']['name'], self.business.name)
        self.assertEqual(stats['by_category']['marketing']['count'], 2)

