from types import SimpleNamespace

import pytest
from django.test import override_settings

from apps.telegram_integration.exceptions import (
    TelegramConfigurationError,
    TelegramProviderError,
)
from apps.telegram_integration.providers.bot_api import TelegramBotAPIProvider
from apps.telegram_integration.providers.mock import (
    MockTelegramProvider,
    TelegramSendResult,
)
from apps.telegram_integration.services import get_telegram_provider


class RecordingHTTPClient:
    def __init__(self, *, body=None, error=None):
        self.body = body or {"ok": True, "result": {}}
        self.error = error
        self.requests = []

    def post(self, url, **kwargs):
        self.requests.append((url, kwargs))
        if self.error:
            raise self.error
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: self.body)


@override_settings(TELEGRAM_PROVIDER="mock")
def test_mock_provider_needs_no_external_token():
    assert isinstance(get_telegram_provider(), MockTelegramProvider)


@override_settings(TELEGRAM_PROVIDER="bot_api", TELEGRAM_BOT_TOKEN="")
def test_bot_api_provider_requires_token():
    with pytest.raises(TelegramConfigurationError, match="TELEGRAM_BOT_TOKEN"):
        get_telegram_provider()


@override_settings(TELEGRAM_PROVIDER="unsupported")
def test_factory_rejects_unsupported_provider_without_chained_error():
    with pytest.raises(
        TelegramConfigurationError, match="Unsupported TELEGRAM_PROVIDER"
    ) as captured:
        get_telegram_provider()

    assert captured.value.__cause__ is None
    assert captured.value.__context__ is None


def test_get_me_uses_official_https_bot_api():
    client = RecordingHTTPClient(
        body={"ok": True, "result": {"id": 123, "username": "ethical_bot"}}
    )

    identity = TelegramBotAPIProvider(token="test-token", client=client).get_me()

    assert identity == {"id": 123, "username": "ethical_bot"}
    assert client.requests == [
        (
            "https://api.telegram.org/bottest-token/getMe",
            {"json": {}, "timeout": 10.0},
        )
    ]


def test_send_message_normalizes_provider_result():
    client = RecordingHTTPClient(body={"ok": True, "result": {"message_id": 456}})

    result = TelegramBotAPIProvider(token="test-token", client=client).send_message(
        chat_id="-1001", text="Hello"
    )

    assert result == TelegramSendResult(
        provider_message_id="456", delivery_state="sent"
    )
    assert client.requests[0][1]["json"] == {"chat_id": "-1001", "text": "Hello"}


def test_set_webhook_sends_url_and_secret_token():
    client = RecordingHTTPClient(body={"ok": True, "result": True})

    result = TelegramBotAPIProvider(token="test-token", client=client).set_webhook(
        url="https://app.example.com/api/v1/telegram/webhook/connection-id/",
        secret_token="webhook-secret",
    )

    assert result is True
    assert client.requests[0][1]["json"] == {
        "url": "https://app.example.com/api/v1/telegram/webhook/connection-id/",
        "secret_token": "webhook-secret",
    }


def test_bot_api_error_never_contains_or_chains_token():
    token = "super-secret-token"
    client = RecordingHTTPClient(error=RuntimeError(f"failed URL contains {token}"))
    provider = TelegramBotAPIProvider(token=token, client=client)

    with pytest.raises(
        TelegramProviderError, match="Telegram Bot API request failed"
    ) as captured:
        provider.get_me()

    assert token not in str(captured.value)
    assert captured.value.__cause__ is None
    assert captured.value.__context__ is None


def test_bot_api_rejection_is_sanitized():
    token = "super-secret-token"
    client = RecordingHTTPClient(
        body={"ok": False, "description": f"bad token {token}"}
    )

    with pytest.raises(
        TelegramProviderError, match="Telegram Bot API rejected the request"
    ) as captured:
        TelegramBotAPIProvider(token=token, client=client).get_me()

    assert token not in str(captured.value)
    assert captured.value.__cause__ is None
    assert captured.value.__context__ is None
