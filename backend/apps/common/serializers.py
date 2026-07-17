from rest_framework import serializers

from apps.workspaces.models import WorkspaceMembership


class WorkspaceScopedSerializerMixin:
    """Blocks writing an object into a workspace the requester isn't an active member of.

    Applies on both create and update: if a `workspace` value is supplied, the caller
    must be an active member of that (active) workspace, otherwise it is rejected —
    closing the cross-tenant IDOR on `fields = "__all__"` serializers.
    """

    def validate_workspace(self, workspace):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        is_member = bool(
            user
            and user.is_authenticated
            and WorkspaceMembership.objects.filter(
                user=user,
                workspace=workspace,
                is_active=True,
                workspace__is_active=True,
            ).exists()
        )
        if not is_member:
            raise serializers.ValidationError("Bu ish maydoniga ruxsatingiz yo'q.")
        return workspace
