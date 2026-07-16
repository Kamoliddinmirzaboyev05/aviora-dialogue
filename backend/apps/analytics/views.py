from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.consent.models import ConsentRecord
from apps.conversations.models import Message
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity, ResponseDraft
from apps.workspaces.models import Workspace


class OverviewAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = Workspace.objects.get(id=request.query_params["workspace"], memberships__user=request.user)
        opportunities = Opportunity.objects.filter(workspace=workspace).count()
        leads = Lead.objects.filter(workspace=workspace).count()
        consent_granted = ConsentRecord.objects.filter(workspace=workspace, status=ConsentRecord.Status.GRANTED).count()
        data = {
            "messages_analyzed": Message.objects.filter(workspace=workspace, direction="inbound").count(),
            "opportunities": opportunities,
            "pending_approvals": ResponseDraft.objects.filter(workspace=workspace, status=ResponseDraft.Status.DRAFT).count(),
            "permission_requests_sent": ResponseDraft.objects.filter(workspace=workspace, status=ResponseDraft.Status.SENT).count(),
            "consent_granted": consent_granted,
            "leads": leads,
            "conversion_rate": round((leads / opportunities) * 100, 2) if opportunities else 0,
        }
        return Response(data)
