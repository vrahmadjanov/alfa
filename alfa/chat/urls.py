"""
URL маршруты для Chat API
"""
from django.urls import path

from chat.views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageCreateView,
    MessageListView,
    ConversationStatsView
)

app_name = 'chat'

urlpatterns = [
    # Диалоги
    path('conversations/', ConversationListCreateView.as_view(), name='conversation_list_create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    
    # Сообщения
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message_list'),
    path('conversations/<int:conversation_id>/messages/send/', MessageCreateView.as_view(), name='message_send'),
    
    # Статистика
    path('stats/', ConversationStatsView.as_view(), name='stats'),
]

