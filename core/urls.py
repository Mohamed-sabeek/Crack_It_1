
from django.urls import path
from core.views_ai import CrackItAIChatAPIView, DeleteAIChatHistoryAPIView
from core.views import ai_chat_view, save_ai_chat_history

app_name = 'core'

urlpatterns = [
    # Frontend AI chat page
    path('ai-chat/', ai_chat_view, name='ai-chat-html'),

    # AI chat API endpoint
    path('api/ai-chat/', CrackItAIChatAPIView.as_view(), name='api-ai-chat'),

    # AI chat history endpoints
    path('api/ai-chat-history/', save_ai_chat_history, name='ai-chat-history'),
    path('api/ai-chat-history/<int:chat_id>/', DeleteAIChatHistoryAPIView.as_view(), name='ai-chat-history-delete'),
]
