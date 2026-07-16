from rest_framework import serializers

from apps.triggers.models import TriggerSet


class TriggerSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerSet
        fields = "__all__"
