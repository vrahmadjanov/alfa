"""
Unit и API тесты для управления бизнесами
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Business, BusinessProfile


class BusinessCreateAPITest(APITestCase):
    """
    Тесты для создания бизнеса
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.create_url = reverse('users:business_list_create')
        
        self.valid_payload = {
            'name': 'Моя Кофейня',
            'business_type': 'cafe',
            'description': 'Уютная кофейня в центре',
            'email': 'cafe@example.com',
            'city': 'Москва'
        }
    
    def test_create_business_success(self):
        """Тест успешного создания бизнеса"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(self.create_url, data=self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['name'], self.valid_payload['name'])
        self.assertEqual(response.data['data']['business_type'], self.valid_payload['business_type'])
        
        # Проверяем, что бизнес создан в БД
        self.assertTrue(Business.objects.filter(name=self.valid_payload['name']).exists())
        
        # Проверяем, что профиль создан автоматически
        business = Business.objects.get(name=self.valid_payload['name'])
        self.assertTrue(hasattr(business, 'profile'))
    
    def test_create_business_without_auth(self):
        """Тест создания без аутентификации"""
        response = self.client.post(self.create_url, data=self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_business_duplicate_name(self):
        """Тест создания с дублирующимся названием"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Создаем первый бизнес
        Business.objects.create(
            owner=self.user,
            name=self.valid_payload['name'],
            business_type='cafe'
        )
        
        # Пытаемся создать второй с тем же названием
        response = self.client.post(self.create_url, data=self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('name', response.data['errors'])
    
    def test_create_business_missing_required_fields(self):
        """Тест создания без обязательных полей"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(self.create_url, data={}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('name', response.data['errors'])
        self.assertIn('business_type', response.data['errors'])


class BusinessListAPITest(APITestCase):
    """
    Тесты для получения списка бизнесов
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
        
        # Создаем бизнесы для user1
        self.business1 = Business.objects.create(
            owner=self.user1,
            name='Кофейня 1',
            business_type='cafe',
            city='Москва'
        )
        self.business2 = Business.objects.create(
            owner=self.user1,
            name='Кофейня 2',
            business_type='cafe',
            city='Москва'
        )
        
        # Создаем бизнес для user2
        self.business3 = Business.objects.create(
            owner=self.user2,
            name='Салон красоты',
            business_type='beauty_salon',
            city='Санкт-Петербург'
        )
        
        self.refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(self.refresh.access_token)
        
        self.list_url = reverse('users:business_list_create')
    
    def test_list_businesses_success(self):
        """Тест получения списка своих бизнесов"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)  # Только бизнесы user1
    
    def test_list_businesses_without_auth(self):
        """Тест получения списка без аутентификации"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BusinessDetailAPITest(APITestCase):
    """
    Тесты для работы с конкретным бизнесом
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
        
        self.business = Business.objects.create(
            owner=self.user,
            name='Моя Кофейня',
            business_type='cafe',
            description='Описание',
            city='Москва'
        )
        BusinessProfile.objects.create(business=self.business)
        
        self.other_business = Business.objects.create(
            owner=self.other_user,
            name='Чужая Кофейня',
            business_type='cafe'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.detail_url = reverse('users:business_detail', kwargs={'pk': self.business.id})
        self.other_detail_url = reverse('users:business_detail', kwargs={'pk': self.other_business.id})
    
    def test_get_business_detail_success(self):
        """Тест получения детальной информации о бизнесе"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], self.business.name)
        self.assertIn('profile', response.data['data'])
    
    def test_get_other_user_business(self):
        """Тест попытки получить чужой бизнес"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.other_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_business_success(self):
        """Тест успешного обновления бизнеса"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        update_data = {
            'name': 'Обновленное название',
            'description': 'Новое описание'
        }
        
        response = self.client.patch(self.detail_url, data=update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], update_data['name'])
        
        # Проверяем обновление в БД
        self.business.refresh_from_db()
        self.assertEqual(self.business.name, update_data['name'])
    
    def test_delete_business_archives(self):
        """Тест архивирования бизнеса при удалении"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Проверяем, что бизнес архивирован, а не удален
        self.business.refresh_from_db()
        self.assertEqual(self.business.status, Business.Status.ARCHIVED)


class BusinessProfileAPITest(APITestCase):
    """
    Тесты для работы с профилем бизнеса
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        
        self.business = Business.objects.create(
            owner=self.user,
            name='Моя Кофейня',
            business_type='cafe'
        )
        self.profile = BusinessProfile.objects.create(
            business=self.business,
            employees_count=5
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.profile_url = reverse('users:business_profile', kwargs={'pk': self.business.id})
    
    def test_get_business_profile(self):
        """Тест получения профиля бизнеса"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['employees_count'], 5)
    
    def test_update_business_profile(self):
        """Тест обновления профиля бизнеса"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        update_data = {
            'employees_count': 10,
            'business_context': 'Дополнительный контекст для AI'
        }
        
        response = self.client.patch(self.profile_url, data=update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['employees_count'], 10)
        
        # Проверяем обновление в БД
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.employees_count, 10)


class BusinessStatsAPITest(APITestCase):
    """
    Тесты для получения статистики бизнеса
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='TestPassword123!'
        )
        
        self.business = Business.objects.create(
            owner=self.user,
            name='Моя Кофейня',
            business_type='cafe'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        
        self.stats_url = reverse('users:business_stats', kwargs={'pk': self.business.id})
    
    def test_get_business_stats(self):
        """Тест получения статистики бизнеса"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('business_id', response.data['data'])
        self.assertIn('business_name', response.data['data'])

