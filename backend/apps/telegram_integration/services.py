from django.conf import settings

from apps.telegram_integration.providers.mock import MockTelegramProvider


def get_telegram_provider():
    return MockTelegramProvider()
