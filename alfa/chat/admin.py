"""
Django Admin для управления чатами и сообщениями
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from chat.models import Conversation, Message


class MessageInline(admin.TabularInline):
    """Inline для сообщений в диалоге"""
    model = Message
    extra = 0
    fields = ('role', 'content_preview', 'model', 'tokens_used', 'created_at')
    readonly_fields = ('content_preview', 'created_at')
    can_delete = False
    
    def content_preview(self, obj):
        """Краткое превью содержимого"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Содержимое'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Админ панель для диалогов"""
    
    list_display = ('id', 'title_preview', 'user', 'business', 'category', 'status', 
                    'messages_count', 'last_message_at', 'created_at')
    list_filter = ('status', 'category', 'created_at', 'last_message_at')
    search_fields = ('title', 'user__email', 'business__name')
    readonly_fields = ('created_at', 'updated_at', 'last_message_at', 'messages_count')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'business', 'title', 'category', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'last_message_at'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MessageInline]
    
    def title_preview(self, obj):
        """Краткое превью заголовка"""
        title = obj.title or f'Диалог #{obj.id}'
        return title[:50] + '...' if len(title) > 50 else title
    title_preview.short_description = 'Заголовок'
    
    def messages_count(self, obj):
        """Количество сообщений"""
        return obj.get_messages_count()
    messages_count.short_description = 'Сообщений'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админ панель для сообщений"""
    
    list_display = ('id', 'conversation_link', 'role', 'content_preview', 
                    'model', 'tokens_used', 'response_time', 'created_at')
    list_filter = ('role', 'model', 'created_at')
    search_fields = ('content', 'conversation__title', 'conversation__user__email')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('conversation', 'role', 'content')
        }),
        ('LLM Информация', {
            'fields': ('model', 'tokens_used', 'response_time'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'metadata'),
            'classes': ('collapse',)
        }),
    )
    
    def conversation_link(self, obj):
        """Ссылка на диалог"""
        return obj.conversation.title or f'Диалог #{obj.conversation.id}'
    conversation_link.short_description = 'Диалог'
    
    def content_preview(self, obj):
        """Краткое превью содержимого"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Содержимое'
