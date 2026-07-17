from django.db import models

from apps.common.crypto import decrypt, encrypt
from apps.common.models import WorkspaceScopedModel


class TelegramConnection(WorkspaceScopedModel):
    name = models.CharField(max_length=180)
    provider = models.CharField(max_length=32, default="mock")
    bot_username = models.CharField(max_length=180, blank=True)
    bot_id = models.CharField(max_length=80, blank=True)
    webhook_url = models.URLField(blank=True)
    webhook_status = models.CharField(max_length=32, default="mock_active")
    is_active = models.BooleanField(default=True)
    last_error = models.TextField(blank=True)
    encrypted_bot_token = models.TextField(blank=True)

    # Userbot (MTProto/Telethon) — shaxsiy akkaunt telefon+kod bilan ulanadi
    mode = models.CharField(max_length=16, default="bot_api")  # bot_api | userbot
    phone = models.CharField(max_length=32, blank=True)
    session_string = models.TextField(blank=True)  # Telethon StringSession
    phone_code_hash = models.CharField(max_length=128, blank=True)  # login start->verify orasida
    login_state = models.CharField(max_length=16, default="idle")  # idle|code_sent|active|error
    auto_reply = models.BooleanField(default=True)  # DM va guruhga avto-javob

    class Meta:
        indexes = [
            models.Index(fields=["mode", "login_state", "is_active"]),
        ]

    def set_session(self, plaintext: str):
        self.session_string = encrypt(plaintext)

    def get_session(self) -> str:
        return decrypt(self.session_string)


class TelegramChat(WorkspaceScopedModel):
    connection = models.ForeignKey(TelegramConnection, on_delete=models.CASCADE, related_name="chats")
    title = models.CharField(max_length=180)
    chat_type = models.CharField(max_length=32, default="group")
    telegram_chat_id = models.CharField(max_length=80)
    monitoring_enabled = models.BooleanField(default=True)
    admin_approved = models.BooleanField(default=True)
    reply_mode = models.CharField(max_length=32, default="approval")
    minimum_score = models.PositiveIntegerField(default=50)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["workspace", "telegram_chat_id"], name="unique_chat_per_workspace")]


class TelegramContact(WorkspaceScopedModel):
    telegram_user_id = models.CharField(max_length=80)
    display_name = models.CharField(max_length=180)
    username = models.CharField(max_length=180, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["workspace", "telegram_user_id"], name="unique_contact_per_workspace")]


class TelegramUpdate(WorkspaceScopedModel):
    connection = models.ForeignKey(TelegramConnection, on_delete=models.CASCADE)
    update_id = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=32, default="processed")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["connection", "update_id"], name="unique_update_per_connection")]
