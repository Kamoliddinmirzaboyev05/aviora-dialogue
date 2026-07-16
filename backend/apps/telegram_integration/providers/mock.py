from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class TelegramSendResult:
    provider_message_id: str
    delivery_state: str


class MockTelegramProvider:
    def get_me(self) -> dict:
        return {"id": "mock-bot", "username": "mock_telegram_bot"}

    def send_message(self, *, chat_id: str, text: str) -> TelegramSendResult:
        return TelegramSendResult(provider_message_id=f"mock-{uuid4()}", delivery_state="sent")

    def set_webhook(self, *, url: str, secret_token: str) -> bool:
        return True
