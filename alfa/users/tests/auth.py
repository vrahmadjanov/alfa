"""
Unit и API тесты для аутентификации пользователей
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Business


class UserRegistrationAPITest(APITestCase):
    """
    Тесты для регистрации пользователей
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.register_url = reverse('users:register')
        self.valid_payload = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Иван',
            'last_name': 'Иванов'
        }
    
    def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(
            self.register_url,
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.valid_payload['email'])
        self.assertEqual(response.data['data']['user']['first_name'], self.valid_payload['first_name'])
        
        # Проверяем, что пользователь создан в БД
        self.assertTrue(User.objects.filter(email=self.valid_payload['email']).exists())
    
    def test_register_user_without_names(self):
        """Тест регистрации без имени и фамилии (опциональные поля)"""
        payload = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['user']['first_name'], '')
        self.assertEqual(response.data['data']['user']['last_name'], '')
    
    def test_register_user_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        payload = self.valid_payload.copy()
        payload['password_confirm'] = 'DifferentPassword123!'
        
        response = self.client.post(self.register_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
        self.assertIn('password', response.data['errors'])
    
    def test_register_user_invalid_email(self):
        """Тест регистрации с невалидным email"""
        payload = self.valid_payload.copy()
        payload['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['errors'])
    
    def test_register_user_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        # Создаем пользователя
        User.objects.create_user(
            email=self.valid_payload['email'],
            password='SomePassword123!'
        )
        
        response = self.client.post(self.register_url, data=self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['errors'])
    
    def test_register_user_weak_password(self):
        """Тест регистрации со слабым паролем"""
        payload = self.valid_payload.copy()
        payload['password'] = '123'
        payload['password_confirm'] = '123'
        
        response = self.client.post(self.register_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('password', response.data['errors'])
    
    def test_register_user_missing_required_fields(self):
        """Тест регистрации без обязательных полей"""
        response = self.client.post(self.register_url, data={}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['errors'])
        self.assertIn('password', response.data['errors'])


class UserLoginAPITest(APITestCase):
    """
    Тесты для авторизации пользователей
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.login_url = reverse('users:login')
        self.email = 'testuser@example.com'
        self.password = 'TestPassword123!'
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name='Test',
            last_name='User'
        )
    
    def test_login_success(self):
        """Тест успешной авторизации"""
        payload = {
            'email': self.email,
            'password': self.password
        }
        
        response = self.client.post(self.login_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.email)
    
    def test_login_wrong_password(self):
        """Тест авторизации с неверным паролем"""
        payload = {
            'email': self.email,
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_nonexistent_user(self):
        """Тест авторизации несуществующего пользователя"""
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        
        response = self.client.post(self.login_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_inactive_user(self):
        """Тест авторизации деактивированного пользователя"""
        self.user.is_active = False
        self.user.save()
        
        payload = {
            'email': self.email,
            'password': self.password
        }
        
        response = self.client.post(self.login_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_credentials(self):
        """Тест авторизации без credentials"""
        response = self.client.post(self.login_url, data={}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['errors'])
        self.assertIn('password', response.data['errors'])


class UserLogoutAPITest(APITestCase):
    """
    Тесты для выхода из системы
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.logout_url = reverse('users:logout')
        
        # Создаем пользователя и получаем токены
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPassword123!'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)
    
    def test_logout_success(self):
        """Тест успешного выхода из системы"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {'refresh': self.refresh_token}
        response = self.client.post(self.logout_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('message', response.data)
    
    def test_logout_without_refresh_token(self):
        """Тест выхода без refresh токена"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(self.logout_url, data={}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_logout_without_authentication(self):
        """Тест выхода без аутентификации"""
        payload = {'refresh': self.refresh_token}
        response = self.client.post(self.logout_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_with_invalid_refresh_token(self):
        """Тест выхода с невалидным refresh токеном"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {'refresh': 'invalid_token_here'}
        response = self.client.post(self.logout_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshAPITest(APITestCase):
    """
    Тесты для обновления токенов
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.refresh_url = reverse('users:token_refresh')
        
        # Создаем пользователя и получаем токены
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPassword123!'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
    
    def test_token_refresh_success(self):
        """Тест успешного обновления токена"""
        payload = {'refresh': self.refresh_token}
        response = self.client.post(self.refresh_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh_invalid_token(self):
        """Тест обновления с невалидным токеном"""
        payload = {'refresh': 'invalid_token'}
        response = self.client.post(self.refresh_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh_missing_token(self):
        """Тест обновления без токена"""
        response = self.client.post(self.refresh_url, data={}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VerifyTokenAPITest(APITestCase):
    """
    Тесты для проверки валидности токенов
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.verify_url = reverse('users:verify_token')
        
        # Создаем пользователя и получаем токены
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
    
    def test_verify_valid_token(self):
        """Тест проверки валидного токена"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertTrue(response.data['data']['valid'])
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.user.email)
    
    def test_verify_without_token(self):
        """Тест проверки без токена"""
        response = self.client.get(self.verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_verify_invalid_token(self):
        """Тест проверки с невалидным токеном"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        response = self.client.get(self.verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CurrentUserAPITest(APITestCase):
    """
    Тесты для получения и обновления текущего пользователя
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.me_url = reverse('users:current_user')
        
        # Создаем пользователя и получаем токены
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        # Создаем бизнес для пользователя
        self.business = Business.objects.create(
            owner=self.user,
            name='Тестовая Кофейня',
            business_type='cafe',
            city='Москва'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
    
    def test_get_current_user_success(self):
        """Тест получения информации о текущем пользователе"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['email'], self.user.email)
        self.assertEqual(response.data['data']['first_name'], self.user.first_name)
        self.assertEqual(response.data['data']['last_name'], self.user.last_name)
        self.assertIn('businesses', response.data['data'])
        self.assertEqual(len(response.data['data']['businesses']), 1)
        self.assertEqual(response.data['data']['businesses'][0]['name'], 'Тестовая Кофейня')
    
    def test_get_current_user_without_authentication(self):
        """Тест получения пользователя без аутентификации"""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_current_user_success(self):
        """Тест обновления информации о текущем пользователе"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {
            'first_name': 'Новое Имя',
            'last_name': 'Новая Фамилия'
        }
        
        response = self.client.patch(self.me_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['first_name'], 'Новое Имя')
        self.assertEqual(response.data['data']['last_name'], 'Новая Фамилия')
        
        # Проверяем, что данные обновились в БД
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Новое Имя')
        self.assertEqual(self.user.last_name, 'Новая Фамилия')
    
    def test_update_current_user_partial(self):
        """Тест частичного обновления пользователя"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        payload = {'first_name': 'Только Имя'}
        
        response = self.client.patch(self.me_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['first_name'], 'Только Имя')
        self.assertEqual(response.data['data']['last_name'], 'User')  # Не изменилось
    
    def test_update_current_user_readonly_fields(self):
        """Тест попытки изменить read-only поля"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        original_email = self.user.email
        payload = {
            'email': 'newemail@example.com',  # Read-only
            'is_email_verified': True  # Read-only
        }
        
        response = self.client.patch(self.me_url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Email не должен измениться
        self.assertEqual(response.data['data']['email'], original_email)
        # is_email_verified не должен измениться
        self.assertFalse(response.data['data']['is_email_verified'])


class AuthenticationFlowIntegrationTest(APITestCase):
    """
    Интеграционные тесты для полного flow аутентификации
    """
    
    def test_complete_authentication_flow(self):
        """
        Тест полного цикла: регистрация -> логин -> получение профиля -> 
        обновление профиля -> обновление токена -> выход
        """
        # 1. Регистрация
        register_url = reverse('users:register')
        register_payload = {
            'email': 'flowtest@example.com',
            'password': 'FlowTest123!',
            'password_confirm': 'FlowTest123!',
            'first_name': 'Flow',
            'last_name': 'Test'
        }
        
        register_response = self.client.post(
            register_url,
            data=register_payload,
            format='json'
        )
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(register_response.data['success'])
        access_token = register_response.data['data']['access']
        refresh_token = register_response.data['data']['refresh']
        
        # 2. Получение профиля
        me_url = reverse('users:current_user')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        me_response = self.client.get(me_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertTrue(me_response.data['success'])
        self.assertEqual(me_response.data['data']['email'], 'flowtest@example.com')
        
        # 3. Обновление профиля
        update_payload = {'first_name': 'Updated'}
        update_response = self.client.patch(me_url, data=update_payload, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertTrue(update_response.data['success'])
        self.assertEqual(update_response.data['data']['first_name'], 'Updated')
        
        # 4. Обновление токена
        refresh_url = reverse('users:token_refresh')
        refresh_payload = {'refresh': refresh_token}
        
        refresh_response = self.client.post(
            refresh_url,
            data=refresh_payload,
            format='json'
        )
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_access_token = refresh_response.data['access']
        new_refresh_token = refresh_response.data['refresh']
        
        # 5. Проверка нового токена
        verify_url = reverse('users:verify_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        verify_response = self.client.get(verify_url)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertTrue(verify_response.data['success'])
        self.assertTrue(verify_response.data['data']['valid'])
        
        # 6. Выход из системы
        logout_url = reverse('users:logout')
        logout_payload = {'refresh': new_refresh_token}
        
        logout_response = self.client.post(
            logout_url,
            data=logout_payload,
            format='json'
        )
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertTrue(logout_response.data['success'])
        
        # 7. Проверка, что старый refresh токен больше не работает
        refresh_again_response = self.client.post(
            refresh_url,
            data={'refresh': new_refresh_token},
            format='json'
        )
        
        self.assertEqual(refresh_again_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_after_registration(self):
        """Тест логина после регистрации"""
        # Регистрация
        register_url = reverse('users:register')
        email = 'logintest@example.com'
        password = 'LoginTest123!'
        
        register_payload = {
            'email': email,
            'password': password,
            'password_confirm': password
        }
        
        self.client.post(register_url, data=register_payload, format='json')
        
        # Логин с теми же credentials
        login_url = reverse('users:login')
        login_payload = {
            'email': email,
            'password': password
        }
        
        login_response = self.client.post(login_url, data=login_payload, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue(login_response.data['success'])
        self.assertIn('access', login_response.data['data'])
        self.assertIn('refresh', login_response.data['data'])

