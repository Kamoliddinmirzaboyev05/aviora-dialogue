from django.db import models

from apps.common.models import WorkspaceScopedModel


class AIRequestLog(WorkspaceScopedModel):
    provider = models.CharField(max_length=32)
    model = models.CharField(max_length=120, blank=True)
    purpose = models.CharField(max_length=80)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    succeeded = models.BooleanField(default=True)
    concise_reason = models.TextField(blank=True)
