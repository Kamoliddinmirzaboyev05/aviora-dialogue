from django.urls import path

from apps.telegram_integration.views import SimulateMessageView, TelegramChatListView, TelegramConnectionListView


urlpatterns = [
    path("connections/", TelegramConnectionListView.as_view(), name="telegram-connections"),
    path("chats/", TelegramChatListView.as_view(), name="telegram-chats"),
    path("simulate-message/", SimulateMessageView.as_view(), name="simulate-message"),
]
