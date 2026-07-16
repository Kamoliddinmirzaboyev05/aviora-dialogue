from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.conversations.models import Conversation
from apps.leads.models import Lead
from apps.opportunities.serializers import LeadSerializer
from apps.opportunities.services import convert_conversation_to_lead
from apps.workspaces.models import Workspace


class LeadListView(ListAPIView):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lead.objects.filter(workspace__memberships__user=self.request.user).order_by("-created_at")


class LeadUpdateView(UpdateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Lead.objects.filter(workspace__memberships__user=self.request.user)


class ConvertLeadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = Workspace.objects.get(id=request.data["workspace"], memberships__user=request.user)
        conversation = Conversation.objects.get(id=request.data["conversation"], workspace=workspace)
        lead = convert_conversation_to_lead(workspace=workspace, conversation=conversation, actor=request.user)
        return Response(LeadSerializer(lead).data, status=status.HTTP_201_CREATED)
