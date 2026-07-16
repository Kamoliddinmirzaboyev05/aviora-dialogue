from django.db import models

from apps.common.models import TimestampedModel, WorkspaceScopedModel


class Plan(TimestampedModel):
    name = models.CharField(max_length=120, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    limits = models.JSONField(default=dict, blank=True)


class Subscription(WorkspaceScopedModel):
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=32, default="active")
