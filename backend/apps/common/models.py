import uuid

from django.db import models


class TimestampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WorkspaceScopedModel(TimestampedModel):
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE)

    class Meta:
        abstract = True
