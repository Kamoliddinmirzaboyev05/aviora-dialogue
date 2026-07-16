from rest_framework import serializers


class OverviewAnalyticsSerializer(serializers.Serializer):
    messages_analyzed = serializers.IntegerField()
    opportunities = serializers.IntegerField()
    pending_approvals = serializers.IntegerField()
    permission_requests_sent = serializers.IntegerField()
    consent_granted = serializers.IntegerField()
    leads = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
