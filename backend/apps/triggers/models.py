from django.db import models

from apps.common.models import WorkspaceScopedModel


class TriggerSet(WorkspaceScopedModel):
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    minimum_score = models.PositiveIntegerField(default=50)
    positive_keywords = models.JSONField(default=list, blank=True)
    negative_keywords = models.JSONField(default=list, blank=True)
    positive_examples = models.JSONField(default=list, blank=True)
    negative_examples = models.JSONField(default=list, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["workspace", "name"], name="unique_trigger_set_per_workspace")]
        indexes = [models.Index(fields=["workspace", "enabled"])]

    def __str__(self):
        return self.name
