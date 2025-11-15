"""
WebSocket URL routing для Alfa Business Assistant
"""

from django.urls import path

# Здесь будут подключаться consumers для WebSocket
# from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    # path('ws/chat/<str:conversation_id>/', ChatConsumer.as_asgi()),
]

