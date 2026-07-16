from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class TelegramSendResult:
    provider_message_id: str
    delivery_state: str


class MockTelegramProvider:
    def send_message(self, *, chat_id: str, text: str) -> TelegramSendResult:
        return TelegramSendResult(provider_message_id=f"mock-{uuid4()}", delivery_state="sent")
