from rest_framework import serializers

from apps.workspaces.models import Workspace, WorkspaceMembership


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "name", "slug", "business_name", "industry", "timezone", "default_language", "is_active"]


class MembershipSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer()

    class Meta:
        model = WorkspaceMembership
        fields = ["id", "role", "is_active", "workspace"]
