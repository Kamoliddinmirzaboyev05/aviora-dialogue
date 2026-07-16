from django.db import models

from apps.common.models import WorkspaceScopedModel


class Conversation(WorkspaceScopedModel):
    chat = models.ForeignKey("telegram_integration.TelegramChat", on_delete=models.CASCADE)
    contact = models.ForeignKey("telegram_integration.TelegramContact", on_delete=models.CASCADE)
    opportunity = models.ForeignKey("opportunities.Opportunity", on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True, blank=True)
    consent_status = models.CharField(max_length=32, default="not_requested")
    status = models.CharField(max_length=32, default="open")
    summary = models.TextField(blank=True)


class Message(WorkspaceScopedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    direction = models.CharField(max_length=32)
    body = models.TextField()
    source = models.CharField(max_length=32, default="system")
    delivery_state = models.CharField(max_length=32, default="stored")
    metadata = models.JSONField(default=dict, blank=True)
