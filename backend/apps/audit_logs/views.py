from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.audit_logs.models import AuditLog
from apps.audit_logs.serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AuditLog.objects.filter(workspace__memberships__user=self.request.user).order_by("-created_at")
