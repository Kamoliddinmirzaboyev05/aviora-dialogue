from django.conf import settings
from django.db import models

from apps.common.models import WorkspaceScopedModel


class AuditLog(WorkspaceScopedModel):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=120)
    resource_type = models.CharField(max_length=120)
    resource_id = models.CharField(max_length=120, blank=True)
    summary = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["workspace", "action", "created_at"])]
