from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.opportunities.serializers import OpportunitySerializer, ResponseDraftSerializer
from apps.opportunities.services import simulate_incoming_message
from apps.telegram_integration.models import TelegramChat, TelegramConnection
from apps.telegram_integration.serializers import TelegramChatSerializer, TelegramConnectionSerializer
from apps.workspaces.models import Workspace


class TelegramConnectionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace_id = request.query_params.get("workspace")
        queryset = TelegramConnection.objects.filter(workspace_id=workspace_id, workspace__memberships__user=request.user)
        return Response({"results": TelegramConnectionSerializer(queryset, many=True).data})


class TelegramChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace_id = request.query_params.get("workspace")
        queryset = TelegramChat.objects.filter(workspace_id=workspace_id, workspace__memberships__user=request.user)
        return Response({"results": TelegramChatSerializer(queryset, many=True).data})


class SimulateMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = Workspace.objects.get(id=request.data["workspace"], memberships__user=request.user)
        result = simulate_incoming_message(
            workspace=workspace,
            actor=request.user,
            message=request.data["message"],
            sender_name=request.data.get("sender_name", "Telegram User"),
            telegram_user_id=request.data.get("telegram_user_id", "demo-user"),
        )
        return Response(
            {
                "opportunity": OpportunitySerializer(result["opportunity"]).data if result["opportunity"] else None,
                "draft": ResponseDraftSerializer(result["draft"]).data if result["draft"] else None,
            },
            status=status.HTTP_201_CREATED,
        )
