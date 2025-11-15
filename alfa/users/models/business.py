from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models.user import User

class Business(models.Model):
    """
    Модель предприятия (кофейня, салон, магазин)
    """
    
    class BusinessType(models.TextChoices):
        CAFE = 'cafe', _('Кафе/Кофейня')
        RESTAURANT = 'restaurant', _('Ресторан')
        BEAUTY_SALON = 'beauty_salon', _('Салон красоты')
        BARBERSHOP = 'barbershop', _('Барбершоп')
        RETAIL = 'retail', _('Магазин')
        FITNESS = 'fitness', _('Фитнес/Спорт')
        SERVICES = 'services', _('Услуги')
        OTHER = 'other', _('Другое')
    
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Активен')
        INACTIVE = 'inactive', _('Неактивен')
        ARCHIVED = 'archived', _('Архивирован')
    
    # Основная информация
    name = models.CharField(_('Название'), max_length=255)
    business_type = models.CharField(
        _('Тип бизнеса'),
        max_length=50,
        choices=BusinessType.choices
    )
    description = models.TextField(_('Описание'), blank=True)
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    # Контактная информация
    email = models.EmailField(_('Email'), blank=True)
    
    # Адрес
    city = models.CharField(_('Город'), max_length=100, blank=True)
    
    # Владелец бизнеса
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='businesses',
        verbose_name=_('Владелец')
    )
    
    # Метаданные
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Бизнес')
        verbose_name_plural = _('Бизнесы')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class BusinessProfile(models.Model):
    """
    Детальный профиль бизнеса с метриками и настройками
    """
    
    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Бизнес')
    )
    
    # Базовые операционные данные
    employees_count = models.IntegerField(
        _('Количество сотрудников'),
        default=1
    )
    
    # Дополнительные данные для AI
    business_context = models.TextField(
        _('Контекст бизнеса'),
        blank=True,
        help_text='Дополнительная информация для AI ассистента'
    )
    
    ai_preferences = models.JSONField(
        _('Настройки AI'),
        default=dict,
        blank=True,
        help_text='Предпочтения для работы AI ассистента'
    )
    
    # Метаданные
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль бизнеса')
        verbose_name_plural = _('Профили бизнесов')
    
    def __str__(self):
        return f"Профиль: {self.business.name}"


class BusinessMetrics(models.Model):
    """
    Временные метрики бизнеса (для аналитики и AI)
    Сохраняются периодически для отслеживания динамики
    """
    
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name=_('Бизнес')
    )
    
    # Период
    date = models.DateField(_('Дата'))
    period_type = models.CharField(
        _('Тип периода'),
        max_length=20,
        choices=[
            ('day', 'День'),
            ('week', 'Неделя'),
            ('month', 'Месяц')
        ],
        default='day'
    )
    
    # Финансовые показатели
    revenue = models.DecimalField(
        _('Выручка'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    expenses = models.DecimalField(
        _('Расходы'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    profit = models.DecimalField(
        _('Прибыль'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Клиентские метрики
    customers_count = models.IntegerField(_('Количество клиентов'), default=0)
    transactions_count = models.IntegerField(_('Количество транзакций'), default=0)
    avg_check = models.DecimalField(
        _('Средний чек'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Дополнительные данные (JSON для гибкости)
    additional_data = models.JSONField(
        _('Дополнительные данные'),
        default=dict,
        blank=True,
        help_text='Специфичные для отрасли метрики'
    )
    
    # Метаданные
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Метрика бизнеса')
        verbose_name_plural = _('Метрики бизнеса')
        ordering = ['-date']
        unique_together = ['business', 'date', 'period_type']
    
    def __str__(self):
        return f"{self.business.name} - {self.date}"