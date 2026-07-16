from rest_framework.permissions import BasePermission

from apps.workspaces.models import WorkspaceMembership


class IsWorkspaceMember(BasePermission):
    def has_permission(self, request, view):
        workspace_id = request.query_params.get("workspace") or request.data.get("workspace")
        if not workspace_id:
            return bool(request.user and request.user.is_authenticated)
        return WorkspaceMembership.objects.filter(user=request.user, workspace_id=workspace_id, is_active=True).exists()


def user_workspace_ids(user):
    if not user or not user.is_authenticated:
        return []
    return list(
        WorkspaceMembership.objects.filter(user=user, is_active=True).values_list("workspace_id", flat=True)
    )
