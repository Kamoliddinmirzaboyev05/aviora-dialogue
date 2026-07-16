from django.conf import settings
from django.db import models

from apps.common.models import WorkspaceScopedModel


class Opportunity(WorkspaceScopedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PERMISSION_REQUESTED = "permission_requested", "Permission requested"
        CONSENT_RECEIVED = "consent_received", "Consent received"
        CONVERTED_TO_LEAD = "converted_to_lead", "Converted to lead"

    chat = models.ForeignKey("telegram_integration.TelegramChat", on_delete=models.CASCADE)
    contact = models.ForeignKey("telegram_integration.TelegramContact", on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True, blank=True)
    trigger_set = models.ForeignKey("triggers.TriggerSet", on_delete=models.SET_NULL, null=True, blank=True)
    source_message = models.TextField()
    detected_intent = models.CharField(max_length=120)
    relevance_score = models.PositiveIntegerField(default=0)
    confidence = models.FloatField(default=0)
    concise_reason = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    assigned_reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class ResponseDraft(WorkspaceScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        SENT = "sent", "Sent"
        REJECTED = "rejected", "Rejected"

    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="drafts")
    draft_type = models.CharField(max_length=40, default="permission_request")
    text = models.TextField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    safety_flags = models.JSONField(default=list, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
