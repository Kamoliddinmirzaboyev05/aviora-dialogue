from rest_framework.permissions import BasePermission

from apps.workspaces.models import WorkspaceMembership


class IsWorkspaceMember(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        workspace_id = request.query_params.get("workspace") or request.data.get("workspace")
        if not workspace_id:
            # No workspace scope in the request: allow only so object-level checks below can run.
            return True
        return WorkspaceMembership.objects.filter(
            user=request.user, workspace_id=workspace_id, is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        workspace_id = getattr(obj, "workspace_id", None)
        if workspace_id is None:
            return False
        return workspace_id in user_workspace_ids(request.user)


def user_workspace_ids(user):
    if not user or not user.is_authenticated:
        return []
    return list(
        WorkspaceMembership.objects.filter(user=user, is_active=True).values_list("workspace_id", flat=True)
    )
