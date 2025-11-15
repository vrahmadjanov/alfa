"""
Django Admin для управления пользователями и бизнесами
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User, Business, BusinessProfile, BusinessMetrics


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ панель для пользователей"""
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Личная информация'), {'fields': ('first_name', 'last_name')}),
        (_('Статус'), {'fields': ('is_email_verified',)}),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    list_display = ('email', 'first_name', 'last_name', 'is_email_verified', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_email_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)


class BusinessProfileInline(admin.StackedInline):
    """Inline для профиля бизнеса"""
    model = BusinessProfile
    can_delete = False
    fields = (
        'employees_count',
        'business_context',
        'ai_preferences',
    )


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Админ панель для бизнесов"""
    
    list_display = ('name', 'owner', 'business_type', 'city', 'status', 'created_at')
    list_filter = ('business_type', 'status', 'created_at')
    search_fields = ('name', 'description', 'city', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'name', 'business_type', 'description', 'status')
        }),
        ('Контакты', {
            'fields': ('email', 'city')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BusinessProfileInline]


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    """Админ панель для метрик бизнеса"""
    
    list_display = (
        'business', 'date', 'period_type', 
        'revenue', 'expenses', 'profit', 
        'customers_count', 'avg_check'
    )
    list_filter = ('period_type', 'date', 'business__business_type')
    search_fields = ('business__name',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Период', {
            'fields': ('business', 'date', 'period_type')
        }),
        ('Финансы', {
            'fields': ('revenue', 'expenses', 'profit')
        }),
        ('Клиенты', {
            'fields': ('customers_count', 'transactions_count', 'avg_check')
        }),
        ('Дополнительно', {
            'fields': ('additional_data', 'created_at'),
            'classes': ('collapse',)
        }),
    )
