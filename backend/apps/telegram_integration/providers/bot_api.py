from django.conf import settings
import requests

from apps.telegram_integration.exceptions import (
    TelegramConfigurationError,
    TelegramProviderError,
)
from apps.telegram_integration.providers.mock import TelegramSendResult


class TelegramBotAPIProvider:
    API_BASE_URL = "https://api.telegram.org"

    def __init__(self, *, token: str | None = None, client=None):
        self.token = token if token is not None else settings.TELEGRAM_BOT_TOKEN
        if not self.token:
            raise TelegramConfigurationError(
                "Telegram Bot API provider requires TELEGRAM_BOT_TOKEN."
            )
        self.client = client if client is not None else requests.Session()

    def get_me(self) -> dict:
        return self._post("getMe", {})

    def send_message(self, *, chat_id: str, text: str) -> TelegramSendResult:
        result = self._post("sendMessage", {"chat_id": chat_id, "text": text})
        if not isinstance(result, dict) or "message_id" not in result:
            raise TelegramProviderError(
                "Telegram Bot API returned an invalid response."
            )
        return TelegramSendResult(
            provider_message_id=str(result["message_id"]), delivery_state="sent"
        )

    def set_webhook(self, *, url: str, secret_token: str) -> bool:
        return bool(
            self._post("setWebhook", {"url": url, "secret_token": secret_token})
        )

    def _post(self, method: str, payload: dict):
        body = None
        try:
            response = self.client.post(
                f"{self.API_BASE_URL}/bot{self.token}/{method}",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            body = response.json()
        except Exception:
            pass

        if body is None:
            raise TelegramProviderError("Telegram Bot API request failed.")
        if not isinstance(body, dict) or not body.get("ok") or "result" not in body:
            raise TelegramProviderError("Telegram Bot API rejected the request.")
        return body["result"]
