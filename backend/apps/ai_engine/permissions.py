from apps.workspaces.models import WorkspaceMembership


def get_workspace_admin_membership(request):
    return (
        WorkspaceMembership.objects.filter(
            workspace_id=request.data.get("workspace"),
            user=request.user,
            is_active=True,
            role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
        )
        .select_related("workspace")
        .first()
    )
