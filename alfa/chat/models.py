"""
Модели для чата и сообщений с AI ассистентом
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User, Business


class Conversation(models.Model):
    """
    Модель диалога/сессии чата с AI ассистентом
    """
    
    class Category(models.TextChoices):
        GENERAL = 'general', _('Общее')
        LEGAL = 'legal', _('Юридическая консультация')
        MARKETING = 'marketing', _('Маркетинг')
        FINANCE = 'finance', _('Финансы')
        HR = 'hr', _('Управление персоналом')
        OPERATIONS = 'operations', _('Операционные вопросы')
    
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Активен')
        ARCHIVED = 'archived', _('Архивирован')
        COMPLETED = 'completed', _('Завершен')
    
    # Владелец диалога
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('Пользователь')
    )
    
    # Бизнес, в контексте которого ведется диалог
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('Бизнес'),
        null=True,
        blank=True,
        help_text='Бизнес, для которого ведется диалог (опционально)'
    )
    
    # Информация о диалоге
    title = models.CharField(
        _('Заголовок'),
        max_length=255,
        blank=True,
        help_text='Автоматически генерируется из первого сообщения'
    )
    
    category = models.CharField(
        _('Категория'),
        max_length=50,
        choices=Category.choices,
        default=Category.GENERAL
    )
    
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    # Метаданные
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    last_message_at = models.DateTimeField(
        _('Последнее сообщение'),
        null=True,
        blank=True,
        help_text='Время последнего сообщения в диалоге'
    )
    
    # Дополнительные данные
    metadata = models.JSONField(
        _('Метаданные'),
        default=dict,
        blank=True,
        help_text='Дополнительная информация о диалоге'
    )
    
    class Meta:
        verbose_name = _('Диалог')
        verbose_name_plural = _('Диалоги')
        ordering = ['-last_message_at', '-updated_at']
        indexes = [
            models.Index(fields=['-last_message_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['business', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title or f'Диалог #{self.id}'} ({self.user.email})"
    
    def get_messages_count(self):
        """Возвращает количество сообщений в диалоге"""
        return self.messages.count()
    
    def get_last_message(self):
        """Возвращает последнее сообщение в диалоге"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """
    Модель сообщения в диалоге
    """
    
    class Role(models.TextChoices):
        USER = 'user', _('Пользователь')
        ASSISTANT = 'assistant', _('Ассистент')
        SYSTEM = 'system', _('Система')
    
    # Связь с диалогом
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Диалог')
    )
    
    # Роль отправителя
    role = models.CharField(
        _('Роль'),
        max_length=20,
        choices=Role.choices
    )
    
    # Содержимое сообщения
    content = models.TextField(_('Содержимое'))
    
    # Информация о модели LLM (для ответов ассистента)
    model = models.CharField(
        _('Модель LLM'),
        max_length=100,
        blank=True,
        help_text='Название модели LLM, использованной для генерации ответа'
    )
    
    # Токены использованные для генерации (для статистики)
    tokens_used = models.IntegerField(
        _('Использовано токенов'),
        null=True,
        blank=True,
        help_text='Количество токенов использованных для генерации ответа'
    )
    
    # Время генерации ответа (в секундах)
    response_time = models.FloatField(
        _('Время ответа'),
        null=True,
        blank=True,
        help_text='Время генерации ответа в секундах'
    )
    
    # Метаданные
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    # Дополнительные данные
    metadata = models.JSONField(
        _('Метаданные'),
        default=dict,
        blank=True,
        help_text='Дополнительная информация о сообщении (промпт, параметры и т.д.)'
    )
    
    class Meta:
        verbose_name = _('Сообщение')
        verbose_name_plural = _('Сообщения')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_role_display()}: {preview}"
    
    def save(self, *args, **kwargs):
        """Переопределяем save для обновления last_message_at в диалоге"""
        super().save(*args, **kwargs)
        
        # Обновляем время последнего сообщения и заголовок в диалоге
        if self.conversation:
            self.conversation.last_message_at = self.created_at
            
            # Если это первое сообщение пользователя и нет заголовка
            if not self.conversation.title and self.role == Message.Role.USER:
                # Генерируем заголовок из первых 50 символов
                self.conversation.title = self.content[:50] + ('...' if len(self.content) > 50 else '')
            
            self.conversation.save(update_fields=['last_message_at', 'title', 'updated_at'])
