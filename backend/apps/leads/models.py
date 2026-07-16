from django.conf import settings
from django.db import models

from apps.common.models import WorkspaceScopedModel


class Lead(WorkspaceScopedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        QUALIFIED = "qualified", "Qualified"
        CONTACTED = "contacted", "Contacted"
        MEETING_SCHEDULED = "meeting_scheduled", "Meeting scheduled"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    contact = models.ForeignKey("telegram_integration.TelegramContact", on_delete=models.CASCADE)
    conversation = models.ForeignKey("conversations.Conversation", on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True, blank=True)
    detected_need = models.TextField()
    score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    assigned_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class LeadNote(WorkspaceScopedModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")
    body = models.TextField()
