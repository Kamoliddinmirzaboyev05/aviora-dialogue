from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api import api_error
from apps.consent.serializers import ConsentRecordSerializer
from apps.conversations.models import Conversation
from apps.opportunities.serializers import ConversationSerializer, MessageSerializer
from apps.opportunities.services import generate_product_response, simulate_consent_reply


class ConversationListView(ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(workspace__memberships__user=self.request.user).order_by("-created_at")


class ConversationDetailView(RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(workspace__memberships__user=self.request.user)


class SimulateConsentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        conversation = Conversation.objects.get(id=pk, workspace__memberships__user=request.user)
        consent = simulate_consent_reply(conversation=conversation, message=request.data["message"])
        return Response({"consent": ConsentRecordSerializer(consent).data})


class GenerateProductResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        conversation = Conversation.objects.get(id=pk, workspace__memberships__user=request.user)
        try:
            message = generate_product_response(conversation=conversation)
        except PermissionError as error:
            return api_error("consent_required", str(error), status=403)
        return Response({"message": MessageSerializer(message).data})
