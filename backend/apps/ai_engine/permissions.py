from apps.workspaces.models import WorkspaceMembership


def get_workspace_admin_membership(request, workspace_id):
    return (
        WorkspaceMembership.objects.filter(
            workspace_id=workspace_id,
            user=request.user,
            is_active=True,
            role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
            workspace__is_active=True,
        )
        .select_related("workspace")
        .first()
    )
