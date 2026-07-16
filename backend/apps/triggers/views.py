from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.triggers.models import TriggerSet
from apps.triggers.serializers import TriggerSetSerializer


class TriggerSetListCreateView(ListCreateAPIView):
    serializer_class = TriggerSetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TriggerSet.objects.filter(workspace__memberships__user=self.request.user).order_by("name")


class TriggerSetDetailView(RetrieveUpdateAPIView):
    serializer_class = TriggerSetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TriggerSet.objects.filter(workspace__memberships__user=self.request.user)
