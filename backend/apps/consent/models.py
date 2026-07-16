from django.db import models

from apps.common.models import WorkspaceScopedModel


class ConsentRecord(WorkspaceScopedModel):
    class Status(models.TextChoices):
        NOT_REQUESTED = "not_requested", "Not requested"
        REQUEST_SENT = "request_sent", "Request sent"
        GRANTED = "granted", "Granted"
        DENIED = "denied", "Denied"
        WITHDRAWN = "withdrawn", "Withdrawn"
        EXPIRED = "expired", "Expired"

    contact = models.ForeignKey("telegram_integration.TelegramContact", on_delete=models.CASCADE)
    conversation = models.ForeignKey("conversations.Conversation", on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOT_REQUESTED)
    scope = models.CharField(max_length=120, default="receive_product_recommendation")
    request_message = models.TextField(blank=True)
    response_message = models.TextField(blank=True)
    evidence_reference = models.CharField(max_length=255, blank=True)
    granted_at = models.DateTimeField(null=True, blank=True)
