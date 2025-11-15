"""
Тесты для моделей users приложения
"""
from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from datetime import date, timedelta

from users.models import User, Business, BusinessProfile, BusinessMetrics


class UserModelTests(TestCase):
    """Тесты модели User"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Иван',
            'last_name': 'Иванов'
        }
    
    def test_create_user_with_email(self):
        """Создание пользователя с email"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.last_name, 'Иванов')
        self.assertFalse(user.is_email_verified)
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_email_is_unique(self):
        """Email должен быть уникальным"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_user_str_representation(self):
        """Строковое представление пользователя"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(str(user), 'test@example.com')
    
    def test_user_email_required(self):
        """Email обязателен для создания пользователя"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')
    
    def test_user_ordering(self):
        """Пользователи упорядочены по дате создания (новые первые)"""
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass123'
        )
        
        users = User.objects.all()
        self.assertEqual(users[0], user2)
        self.assertEqual(users[1], user1)
    
    def test_user_has_created_and_updated_timestamps(self):
        """Пользователь имеет временные метки"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)


class BusinessModelTests(TestCase):
    """Тесты модели Business"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        
        self.business_data = {
            'name': 'Кофейня "Утро"',
            'business_type': Business.BusinessType.CAFE,
            'description': 'Уютная кофейня в центре города',
            'owner': self.user,
            'email': 'info@utro.ru',
            'city': 'Москва'
        }
    
    def test_create_business(self):
        """Создание бизнеса"""
        business = Business.objects.create(**self.business_data)
        
        self.assertEqual(business.name, 'Кофейня "Утро"')
        self.assertEqual(business.business_type, Business.BusinessType.CAFE)
        self.assertEqual(business.owner, self.user)
        self.assertEqual(business.status, Business.Status.ACTIVE)
    
    def test_business_owner_required(self):
        """Владелец обязателен для бизнеса"""
        business_data = self.business_data.copy()
        del business_data['owner']
        
        with self.assertRaises(IntegrityError):
            Business.objects.create(**business_data)
    
    def test_business_str_representation(self):
        """Строковое представление бизнеса"""
        business = Business.objects.create(**self.business_data)
        
        self.assertEqual(str(business), 'Кофейня "Утро"')
    
    def test_user_can_have_multiple_businesses(self):
        """Пользователь может иметь несколько бизнесов"""
        business1 = Business.objects.create(**self.business_data)
        
        business2_data = self.business_data.copy()
        business2_data['name'] = 'Салон "Красота"'
        business2_data['business_type'] = Business.BusinessType.BEAUTY_SALON
        business2 = Business.objects.create(**business2_data)
        
        user_businesses = self.user.businesses.all()
        self.assertEqual(user_businesses.count(), 2)
        self.assertIn(business1, user_businesses)
        self.assertIn(business2, user_businesses)
    
    def test_business_cascade_delete_with_owner(self):
        """Бизнес удаляется при удалении владельца"""
        business = Business.objects.create(**self.business_data)
        business_id = business.id
        
        self.user.delete()
        
        with self.assertRaises(Business.DoesNotExist):
            Business.objects.get(id=business_id)
    
    def test_business_types_choices(self):
        """Проверка всех типов бизнеса"""
        expected_types = [
            'cafe', 'restaurant', 'beauty_salon', 'barbershop',
            'retail', 'fitness', 'services', 'other'
        ]
        
        actual_types = [choice[0] for choice in Business.BusinessType.choices]
        
        self.assertEqual(actual_types, expected_types)
    
    def test_business_status_default(self):
        """Статус бизнеса по умолчанию - активен"""
        business = Business.objects.create(**self.business_data)
        
        self.assertEqual(business.status, Business.Status.ACTIVE)
    
    def test_business_ordering(self):
        """Бизнесы упорядочены по дате создания (новые первые)"""
        business1 = Business.objects.create(**self.business_data)
        
        business2_data = self.business_data.copy()
        business2_data['name'] = 'Новый бизнес'
        business2 = Business.objects.create(**business2_data)
        
        businesses = Business.objects.all()
        self.assertEqual(businesses[0], business2)
        self.assertEqual(businesses[1], business1)


class BusinessProfileModelTests(TestCase):
    """Тесты модели BusinessProfile"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        
        self.business = Business.objects.create(
            name='Кофейня "Утро"',
            business_type=Business.BusinessType.CAFE,
            owner=self.user
        )
    
    def test_create_business_profile(self):
        """Создание профиля бизнеса"""
        profile = BusinessProfile.objects.create(
            business=self.business,
            employees_count=5,
            business_context='Специализация на specialty coffee',
            ai_preferences={'tone': 'friendly', 'language': 'ru'}
        )
        
        self.assertEqual(profile.business, self.business)
        self.assertEqual(profile.employees_count, 5)
        self.assertEqual(profile.business_context, 'Специализация на specialty coffee')
        self.assertEqual(profile.ai_preferences['tone'], 'friendly')
    
    def test_business_profile_one_to_one_relationship(self):
        """У бизнеса может быть только один профиль"""
        BusinessProfile.objects.create(business=self.business)
        
        with self.assertRaises(IntegrityError):
            BusinessProfile.objects.create(business=self.business)
    
    def test_business_profile_default_employees_count(self):
        """Количество сотрудников по умолчанию - 1"""
        profile = BusinessProfile.objects.create(business=self.business)
        
        self.assertEqual(profile.employees_count, 1)
    
    def test_business_profile_default_ai_preferences(self):
        """AI preferences по умолчанию - пустой словарь"""
        profile = BusinessProfile.objects.create(business=self.business)
        
        self.assertEqual(profile.ai_preferences, {})
    
    def test_business_profile_str_representation(self):
        """Строковое представление профиля бизнеса"""
        profile = BusinessProfile.objects.create(business=self.business)
        
        self.assertEqual(str(profile), 'Профиль: Кофейня "Утро"')
    
    def test_business_profile_cascade_delete(self):
        """Профиль удаляется при удалении бизнеса"""
        profile = BusinessProfile.objects.create(business=self.business)
        profile_id = profile.id
        
        self.business.delete()
        
        with self.assertRaises(BusinessProfile.DoesNotExist):
            BusinessProfile.objects.get(id=profile_id)
    
    def test_access_profile_through_business(self):
        """Доступ к профилю через связанный бизнес"""
        profile = BusinessProfile.objects.create(
            business=self.business,
            employees_count=10
        )
        
        self.assertEqual(self.business.profile, profile)
        self.assertEqual(self.business.profile.employees_count, 10)


class BusinessMetricsModelTests(TestCase):
    """Тесты модели BusinessMetrics"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        
        self.business = Business.objects.create(
            name='Кофейня "Утро"',
            business_type=Business.BusinessType.CAFE,
            owner=self.user
        )
        
        self.metrics_data = {
            'business': self.business,
            'date': date.today(),
            'period_type': 'day',
            'revenue': Decimal('50000.00'),
            'expenses': Decimal('30000.00'),
            'profit': Decimal('20000.00'),
            'customers_count': 120,
            'transactions_count': 150,
            'avg_check': Decimal('333.33')
        }
    
    def test_create_business_metrics(self):
        """Создание метрик бизнеса"""
        metrics = BusinessMetrics.objects.create(**self.metrics_data)
        
        self.assertEqual(metrics.business, self.business)
        self.assertEqual(metrics.revenue, Decimal('50000.00'))
        self.assertEqual(metrics.profit, Decimal('20000.00'))
        self.assertEqual(metrics.customers_count, 120)
    
    def test_business_metrics_default_values(self):
        """Значения по умолчанию для метрик"""
        metrics = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today()
        )
        
        self.assertEqual(metrics.revenue, Decimal('0'))
        self.assertEqual(metrics.expenses, Decimal('0'))
        self.assertEqual(metrics.profit, Decimal('0'))
        self.assertEqual(metrics.customers_count, 0)
        self.assertEqual(metrics.transactions_count, 0)
        self.assertEqual(metrics.period_type, 'day')
    
    def test_business_can_have_multiple_metrics(self):
        """Бизнес может иметь несколько метрик за разные даты"""
        metrics1 = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today(),
            revenue=Decimal('50000.00')
        )
        
        metrics2 = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today() - timedelta(days=1),
            revenue=Decimal('45000.00')
        )
        
        business_metrics = self.business.metrics.all()
        self.assertEqual(business_metrics.count(), 2)
    
    def test_business_metrics_unique_together(self):
        """Метрики уникальны по бизнесу, дате и типу периода"""
        BusinessMetrics.objects.create(**self.metrics_data)
        
        with self.assertRaises(IntegrityError):
            BusinessMetrics.objects.create(**self.metrics_data)
    
    def test_business_metrics_ordering(self):
        """Метрики упорядочены по дате (новые первые)"""
        metrics1 = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today() - timedelta(days=2),
            revenue=Decimal('40000.00')
        )
        
        metrics2 = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today(),
            revenue=Decimal('50000.00')
        )
        
        metrics = BusinessMetrics.objects.all()
        self.assertEqual(metrics[0], metrics2)
        self.assertEqual(metrics[1], metrics1)
    
    def test_business_metrics_str_representation(self):
        """Строковое представление метрик"""
        metrics = BusinessMetrics.objects.create(**self.metrics_data)
        
        expected = f'Кофейня "Утро" - {date.today()}'
        self.assertEqual(str(metrics), expected)
    
    def test_business_metrics_cascade_delete(self):
        """Метрики удаляются при удалении бизнеса"""
        metrics = BusinessMetrics.objects.create(**self.metrics_data)
        metrics_id = metrics.id
        
        self.business.delete()
        
        with self.assertRaises(BusinessMetrics.DoesNotExist):
            BusinessMetrics.objects.get(id=metrics_id)
    
    def test_business_metrics_additional_data(self):
        """Дополнительные данные в JSON поле"""
        metrics = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today(),
            additional_data={
                'coffee_types': {
                    'espresso': 50,
                    'cappuccino': 40,
                    'latte': 30
                },
                'peak_hours': [9, 10, 11, 14, 15]
            }
        )
        
        self.assertEqual(metrics.additional_data['coffee_types']['espresso'], 50)
        self.assertEqual(len(metrics.additional_data['peak_hours']), 5)
    
    def test_period_type_choices(self):
        """Проверка типов периодов"""
        expected_periods = ['day', 'week', 'month']
        
        actual_periods = [choice[0] for choice in BusinessMetrics._meta.get_field('period_type').choices]
        
        self.assertEqual(actual_periods, expected_periods)


class ModelRelationshipsTests(TestCase):
    """Тесты связей между моделями"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        
        self.business = Business.objects.create(
            name='Тестовый бизнес',
            business_type=Business.BusinessType.CAFE,
            owner=self.user
        )
    
    def test_user_businesses_relationship(self):
        """Связь User -> Business (один ко многим)"""
        business2 = Business.objects.create(
            name='Второй бизнес',
            business_type=Business.BusinessType.RETAIL,
            owner=self.user
        )
        
        self.assertEqual(self.user.businesses.count(), 2)
        self.assertIn(self.business, self.user.businesses.all())
        self.assertIn(business2, self.user.businesses.all())
    
    def test_business_profile_relationship(self):
        """Связь Business -> BusinessProfile (один к одному)"""
        profile = BusinessProfile.objects.create(
            business=self.business,
            employees_count=5
        )
        
        self.assertEqual(self.business.profile, profile)
        self.assertEqual(profile.business, self.business)
    
    def test_business_metrics_relationship(self):
        """Связь Business -> BusinessMetrics (один ко многим)"""
        metrics1 = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today(),
            revenue=Decimal('50000.00')
        )
        
        metrics2 = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today() - timedelta(days=1),
            revenue=Decimal('45000.00')
        )
        
        self.assertEqual(self.business.metrics.count(), 2)
        self.assertIn(metrics1, self.business.metrics.all())
        self.assertIn(metrics2, self.business.metrics.all())
    
    def test_complete_cascade_delete(self):
        """Каскадное удаление всей цепочки"""
        # Создаем полную структуру
        profile = BusinessProfile.objects.create(business=self.business)
        metrics = BusinessMetrics.objects.create(
            business=self.business,
            date=date.today()
        )
        
        business_id = self.business.id
        profile_id = profile.id
        metrics_id = metrics.id
        
        # Удаляем пользователя
        self.user.delete()
        
        # Проверяем, что всё удалилось
        self.assertEqual(Business.objects.filter(id=business_id).count(), 0)
        self.assertEqual(BusinessProfile.objects.filter(id=profile_id).count(), 0)
        self.assertEqual(BusinessMetrics.objects.filter(id=metrics_id).count(), 0)
