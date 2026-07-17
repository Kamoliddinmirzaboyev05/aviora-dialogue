from rest_framework import serializers

from apps.common.serializers import WorkspaceScopedSerializerMixin
from apps.triggers.models import TriggerSet


class TriggerSetSerializer(WorkspaceScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = TriggerSet
        fields = "__all__"
