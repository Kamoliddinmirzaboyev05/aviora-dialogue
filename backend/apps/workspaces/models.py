from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimestampedModel


class Workspace(TimestampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    business_name = models.CharField(max_length=180)
    industry = models.CharField(max_length=120, blank=True)
    timezone = models.CharField(max_length=80, default="Asia/Tashkent")
    default_language = models.CharField(max_length=16, default="uz")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "workspace"
            candidate = base_slug
            counter = 2
            while Workspace.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class WorkspaceMembership(TimestampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        ANALYST = "analyst", "Analyst"
        REVIEWER = "reviewer", "Reviewer"

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_memberships")
    role = models.CharField(max_length=32, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["workspace", "user"], name="unique_workspace_member"),
        ]

    def __str__(self):
        return f"{self.user_id} in {self.workspace_id} as {self.role}"
