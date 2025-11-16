"""
URL маршруты для Chat API
"""
from django.urls import path

from chat.views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageCreateView,
    ConversationStatsView
)

app_name = 'chat'

urlpatterns = [
    # Диалоги
    path('conversations/', ConversationListCreateView.as_view(), name='conversation_list_create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    
    # Сообщения (GET - список, POST - отправить)
    path('conversations/<int:conversation_id>/messages/', MessageCreateView.as_view(), name='messages'),
    
    # Статистика
    path('stats/', ConversationStatsView.as_view(), name='stats'),
]

