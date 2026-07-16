from django.db import models

from apps.common.models import WorkspaceScopedModel


class UsageRecord(WorkspaceScopedModel):
    metric = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=80, blank=True)
