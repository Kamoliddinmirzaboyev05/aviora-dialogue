from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.workspaces.models import Workspace
from apps.workspaces.serializers import WorkspaceSerializer


class WorkspaceListView(ListAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(memberships__user=self.request.user, memberships__is_active=True).distinct().order_by("name")
