from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.opportunities.models import Opportunity, ResponseDraft
from apps.opportunities.serializers import OpportunitySerializer, ResponseDraftSerializer
from apps.opportunities.services import approve_permission_draft


class OpportunityListView(ListAPIView):
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Opportunity.objects.filter(workspace__memberships__user=self.request.user).order_by("-created_at")


class OpportunityDetailView(RetrieveAPIView):
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Opportunity.objects.filter(workspace__memberships__user=self.request.user)


class ApprovalQueueView(ListAPIView):
    serializer_class = ResponseDraftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ResponseDraft.objects.filter(workspace__memberships__user=self.request.user).exclude(status=ResponseDraft.Status.REJECTED).order_by("-created_at")


class ApproveDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        draft = ResponseDraft.objects.get(id=pk, workspace__memberships__user=request.user)
        conversation = approve_permission_draft(draft=draft, actor=request.user)
        return Response(
            {
                "draft": ResponseDraftSerializer(draft).data,
                "conversation": {"id": str(conversation.id), "consent_status": conversation.consent_status},
            },
            status=status.HTTP_200_OK,
        )
