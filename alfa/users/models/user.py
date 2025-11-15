"""
Модели для управления пользователями и их бизнесами
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Менеджер для кастомной модели пользователя с email вместо username
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя с email и паролем
        """
        if not email:
            raise ValueError(_('Email обязателен'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя с email и паролем
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser должен иметь is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя
    Email используется как основной идентификатор вместо username
    """
    
    # Email обязателен и уникален
    email = models.EmailField(
        _('Email адрес'),
        unique=True,
        help_text='Используется для входа в систему'
    )
    
    # Личные данные
    first_name = models.CharField(_('Имя'), max_length=150, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=150, blank=True)
    
    # Статусы
    is_active = models.BooleanField(
        _('Активен'),
        default=True,
        help_text='Отметьте, если пользователь должен считаться активным'
    )
    is_staff = models.BooleanField(
        _('Статус персонала'),
        default=False,
        help_text='Отметьте, если пользователь может входить в админ-панель'
    )
    is_email_verified = models.BooleanField(
        _('Email подтвержден'),
        default=False
    )
    
    # Временные метки
    date_joined = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    created_at = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    objects = UserManager()
    
    # Используем email для входа
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Возвращает first_name и last_name с пробелом между ними
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email
    
    def get_short_name(self):
        """
        Возвращает имя пользователя
        """
        return self.first_name or self.email