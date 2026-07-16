from django.conf import settings
from django.db import transaction

from apps.telegram_integration.exceptions import TelegramConfigurationError
from apps.telegram_integration.models import TelegramChat, TelegramUpdate
from apps.telegram_integration.providers.bot_api import TelegramBotAPIProvider
from apps.telegram_integration.providers.mock import MockTelegramProvider


NON_CLAIMABLE_UPDATE_STATUSES = {"processing", "processed", "ignored", "unsupported"}


def get_telegram_provider():
    provider_name = settings.TELEGRAM_PROVIDER.strip().lower()
    if provider_name == "mock":
        return MockTelegramProvider()
    if provider_name == "bot_api":
        return TelegramBotAPIProvider()
    raise TelegramConfigurationError(f"Unsupported TELEGRAM_PROVIDER: {provider_name}")


def ingest_telegram_update(*, connection, payload: dict):
    update_id = payload.get("update_id")
    if update_id is None:
        return None, False

    update, claimed = _claim_update(
        connection=connection, update_id=update_id, payload=payload
    )
    if not claimed:
        return update, False

    try:
        with transaction.atomic():
            update = TelegramUpdate.objects.select_for_update().get(pk=update.pk)
            return _process_claimed_update(
                update=update, connection=connection, payload=payload
            )
    except Exception:
        _mark_update_failed(update.pk)
        raise


def _claim_update(*, connection, update_id, payload: dict):
    with transaction.atomic():
        update, created = TelegramUpdate.objects.select_for_update().get_or_create(
            connection=connection,
            update_id=str(update_id),
            defaults={
                "workspace": connection.workspace,
                "payload": payload,
                "status": "processing",
            },
        )
        if not created and update.status in NON_CLAIMABLE_UPDATE_STATUSES:
            return update, False
        if not created:
            update.payload = payload
            update.status = "processing"
            update.save(update_fields=["payload", "status", "updated_at"])
        return update, True


def _process_claimed_update(*, update, connection, payload: dict):

    message = payload.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("text"), str):
        _set_update_status(update, "unsupported")
        return update, True

    chat_payload = message.get("chat")
    sender = message.get("from")
    if not isinstance(chat_payload, dict) or not isinstance(sender, dict):
        _set_update_status(update, "unsupported")
        return update, True

    chat_id = chat_payload.get("id")
    sender_id = sender.get("id")
    if chat_id is None or sender_id is None or sender.get("is_bot"):
        _set_update_status(update, "unsupported")
        return update, True

    chat = TelegramChat.objects.filter(
        connection=connection,
        workspace=connection.workspace,
        telegram_chat_id=str(chat_id),
        monitoring_enabled=True,
        admin_approved=True,
    ).first()
    if not connection.is_active or not chat:
        _set_update_status(update, "ignored")
        return update, True

    from apps.opportunities.services import simulate_incoming_message

    simulate_incoming_message(
        workspace=connection.workspace,
        actor=None,
        message=message["text"],
        sender_name=_telegram_display_name(sender),
        telegram_user_id=str(sender_id),
        connection=connection,
        chat=chat,
    )
    _set_update_status(update, "processed")
    return update, True


def _mark_update_failed(update_pk):
    with transaction.atomic():
        update = TelegramUpdate.objects.select_for_update().get(pk=update_pk)
        _set_update_status(update, "failed")


def _telegram_display_name(sender: dict) -> str:
    full_name = " ".join(
        part.strip()
        for part in (
            str(sender.get("first_name", "")),
            str(sender.get("last_name", "")),
        )
        if part.strip()
    )
    return full_name or str(sender.get("username") or "Telegram User")


def _set_update_status(update: TelegramUpdate, status: str):
    update.status = status
    update.save(update_fields=["status", "updated_at"])
