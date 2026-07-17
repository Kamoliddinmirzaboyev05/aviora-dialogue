from django.urls import path

from apps.telegram_integration.views import (
    SimulateMessageView,
    TelegramChatListView,
    TelegramConnectionListView,
    TelegramConnectionTestView,
    TelegramWebhookRegistrationView,
    TelegramWebhookView,
    UserbotStartLoginView,
    UserbotVerifyLoginView,
)


urlpatterns = [
    path("connections/", TelegramConnectionListView.as_view(), name="telegram-connections"),
    path("chats/", TelegramChatListView.as_view(), name="telegram-chats"),
    path("simulate-message/", SimulateMessageView.as_view(), name="simulate-message"),
    path("userbot/start/", UserbotStartLoginView.as_view(), name="userbot-start"),
    path("userbot/verify/", UserbotVerifyLoginView.as_view(), name="userbot-verify"),
    path(
        "test-connection/",
        TelegramConnectionTestView.as_view(),
        name="telegram-test-connection",
    ),
    path(
        "register-webhook/",
        TelegramWebhookRegistrationView.as_view(),
        name="telegram-register-webhook",
    ),
    path(
        "webhook/<uuid:connection_id>/",
        TelegramWebhookView.as_view(),
        name="telegram-webhook",
    ),
]
