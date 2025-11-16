"""
Unit тесты для моделей чата
"""
from django.test import TestCase

from users.models import User
from chat.models import Conversation, Message


class ConversationModelTest(TestCase):
    """
    Unit тесты для модели Conversation
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
    
    def test_conversation_string_representation(self):
        """Тест строкового представления диалога"""
        self.conversation.title = 'Тестовый диалог'
        self.assertIn('Тестовый диалог', str(self.conversation))
    
    def test_conversation_without_title(self):
        """Тест диалога без заголовка"""
        str_repr = str(self.conversation)
        self.assertIn(f'Диалог #{self.conversation.id}', str_repr)
    
    def test_get_messages_count(self):
        """Тест подсчета количества сообщений"""
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Test 1'
        )
        Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content='Test 2'
        )
        
        self.assertEqual(self.conversation.get_messages_count(), 2)
    
    def test_get_last_message(self):
        """Тест получения последнего сообщения"""
        msg1 = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='First'
        )
        msg2 = Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content='Second'
        )
        
        last_msg = self.conversation.get_last_message()
        self.assertEqual(last_msg.id, msg2.id)


class MessageModelTest(TestCase):
    """
    Unit тесты для модели Message
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
    
    def test_message_updates_conversation_last_message_at(self):
        """Тест обновления last_message_at при создании сообщения"""
        self.assertIsNone(self.conversation.last_message_at)
        
        message = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Test message'
        )
        
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.last_message_at)
        self.assertEqual(self.conversation.last_message_at, message.created_at)
    
    def test_first_message_sets_conversation_title(self):
        """Тест автоматической установки заголовка из первого сообщения"""
        self.assertEqual(self.conversation.title, '')
        
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content='Это моё первое сообщение'
        )
        
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'Это моё первое сообщение')
    
    def test_long_first_message_truncates_title(self):
        """Тест обрезки длинного заголовка"""
        long_content = 'a' * 100
        
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content=long_content
        )
        
        self.conversation.refresh_from_db()
        self.assertEqual(len(self.conversation.title), 53)  # 50 + '...'
        self.assertTrue(self.conversation.title.endswith('...'))

