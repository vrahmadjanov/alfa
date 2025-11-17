"""
URL маршруты для Chat API
"""
from django.urls import path

from chat.views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageCreateView,
    MessageStatusView,
    ConversationStatsView
)

app_name = 'chat'

urlpatterns = [
    # Диалоги
    path('conversations/', ConversationListCreateView.as_view(), name='conversation_list_create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    
    # Сообщения (GET - список, POST - отправить)
    path('conversations/<int:conversation_id>/messages/', MessageCreateView.as_view(), name='messages'),
    path('conversations/<int:conversation_id>/messages/<int:message_id>/status/', MessageStatusView.as_view(), name='message_status'),
    
    # Статистика
    path('stats/', ConversationStatsView.as_view(), name='stats'),
]

