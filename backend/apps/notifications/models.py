from django.conf import settings
from django.db import models

from apps.common.models import WorkspaceScopedModel


class Notification(WorkspaceScopedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=80)
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
