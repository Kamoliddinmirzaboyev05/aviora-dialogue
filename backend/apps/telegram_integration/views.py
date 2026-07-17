from uuid import UUID
import secrets

from asgiref.sync import async_to_sync
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api import api_error
from apps.opportunities.serializers import OpportunitySerializer, ResponseDraftSerializer
from apps.opportunities.services import simulate_incoming_message
from apps.telegram_integration.exceptions import (
    TelegramConfigurationError,
    TelegramProviderError,
)
from apps.telegram_integration.models import TelegramChat, TelegramConnection
from apps.telegram_integration.serializers import TelegramChatSerializer, TelegramConnectionSerializer
from apps.telegram_integration.services import (
    get_telegram_provider,
    ingest_telegram_update,
)
from apps.telegram_integration.userbot.login import start_login, verify_login
from apps.workspaces.models import Workspace, WorkspaceMembership


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


class TelegramWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, connection_id):
        expected_secret = settings.TELEGRAM_WEBHOOK_SECRET
        supplied_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if (
            not expected_secret
            or not supplied_secret
            or not secrets.compare_digest(supplied_secret, expected_secret)
        ):
            return api_error(
                "invalid_webhook_secret", "Webhook autentifikatsiyasi muvaffaqiyatsiz tugadi.", status=403
            )

        connection = (
            TelegramConnection.objects.filter(id=connection_id)
            .select_related("workspace")
            .first()
        )
        if not connection:
            return api_error(
                "telegram_connection_not_found",
                "Telegram ulanishi topilmadi.",
                status=404,
            )

        ingest_telegram_update(connection=connection, payload=request.data)
        return Response({"ok": True})


class TelegramConnectionTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership, error_response = _workspace_admin(request)
        if error_response:
            return error_response

        try:
            identity = get_telegram_provider().get_me()
        except (TelegramConfigurationError, TelegramProviderError):
            return api_error(
                "telegram_connection_failed",
                "Telegram provayder ulanish testi muvaffaqiyatsiz tugadi.",
                status=503,
            )

        return Response(
            {
                "state": "connected",
                "bot": {
                    "id": str(identity["id"]),
                    "username": identity.get("username", ""),
                },
            }
        )


class TelegramWebhookRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership, error_response = _workspace_admin(request)
        if error_response:
            return error_response

        connection_id = request.data.get("connection")
        queryset = TelegramConnection.objects.filter(
            workspace=membership.workspace, is_active=True
        )
        if connection_id:
            try:
                connection_id = UUID(str(connection_id))
            except (AttributeError, TypeError, ValueError):
                return api_error(
                    "invalid_connection", "Ulanish yaroqli UUID bo'lishi kerak.", status=400
                )
            queryset = queryset.filter(id=connection_id)
        connection = queryset.order_by("created_at").first()
        if not connection:
            return api_error(
                "telegram_connection_not_found",
                "Faol Telegram ulanishi topilmadi.",
                status=404,
            )

        webhook_secret = settings.TELEGRAM_WEBHOOK_SECRET
        webhook_base_url = settings.TELEGRAM_WEBHOOK_BASE_URL
        if not webhook_secret or not webhook_base_url:
            return api_error(
                "telegram_configuration_error",
                "Telegram webhook sozlamasi to'liq emas.",
                status=503,
            )

        webhook_url = (
            f"{webhook_base_url.rstrip('/')}/api/v1/telegram/webhook/{connection.id}/"
        )
        try:
            registered = get_telegram_provider().set_webhook(
                url=webhook_url, secret_token=webhook_secret
            )
            if not registered:
                raise TelegramProviderError(
                    "Telegram Bot API rejected webhook registration."
                )
        except (TelegramConfigurationError, TelegramProviderError):
            connection.webhook_status = "error"
            connection.last_error = "Telegram webhook ro'yxatdan o'tkazish muvaffaqiyatsiz tugadi."
            connection.save(
                update_fields=["webhook_status", "last_error", "updated_at"]
            )
            return api_error(
                "telegram_webhook_failed",
                "Telegram webhook ro'yxatdan o'tkazish muvaffaqiyatsiz tugadi.",
                status=503,
            )

        connection.webhook_url = webhook_url
        connection.webhook_status = "active"
        connection.last_error = ""
        connection.save(
            update_fields=["webhook_url", "webhook_status", "last_error", "updated_at"]
        )
        return Response({"state": "registered", "webhook_url": webhook_url})


def _workspace_admin(request):
    try:
        workspace_id = UUID(str(request.data.get("workspace")))
    except (AttributeError, TypeError, ValueError):
        return None, api_error(
            "invalid_workspace", "Ish maydoni yaroqli UUID bo'lishi kerak.", status=400
        )

    membership = (
        WorkspaceMembership.objects.filter(
            workspace_id=workspace_id,
            user=request.user,
            is_active=True,
            role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
            workspace__is_active=True,
        )
        .select_related("workspace")
        .first()
    )
    if not membership:
        return None, api_error(
            "workspace_admin_required",
            "Ish maydoni egasi yoki admin ruxsati talab qilinadi.",
            status=403,
        )
    return membership, None


class UserbotStartLoginView(APIView):
    """Userbot login 1-qadam: telefonga kod yuboradi."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership, error_response = _workspace_admin(request)
        if error_response:
            return error_response
        phone = str(request.data.get("phone", "")).strip()
        if not phone:
            return api_error("phone_required", "Telefon raqami kerak.", status=400)

        connection, _ = TelegramConnection.objects.get_or_create(
            workspace=membership.workspace,
            mode="userbot",
            defaults={"name": "Userbot", "provider": "userbot"},
        )
        try:
            result = async_to_sync(start_login)(phone, connection.get_session())
        except Exception as exc:  # noqa: BLE001
            return api_error("telegram_login_failed", str(exc), status=503)

        connection.phone = phone
        connection.set_session(result["session_string"])
        connection.phone_code_hash = result["phone_code_hash"]
        connection.login_state = "code_sent"
        connection.provider = "userbot"
        connection.last_error = ""
        connection.save()
        return Response({"state": "code_sent", "connection": str(connection.id)})


class UserbotVerifyLoginView(APIView):
    """Userbot login 2-qadam: kodni (va kerak bo'lsa 2FA parolni) tasdiqlaydi."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership, error_response = _workspace_admin(request)
        if error_response:
            return error_response
        code = str(request.data.get("code", "")).strip()
        password = str(request.data.get("password", "")).strip()
        if not code:
            return api_error("code_required", "Tasdiqlash kodi kerak.", status=400)

        connection = TelegramConnection.objects.filter(
            workspace=membership.workspace, mode="userbot", login_state="code_sent"
        ).first()
        if not connection:
            return api_error(
                "telegram_login_not_started", "Avval kod so'rang.", status=404
            )
        try:
            result = async_to_sync(verify_login)(
                connection.phone,
                code,
                connection.phone_code_hash,
                connection.get_session(),
                password,
            )
        except Exception as exc:  # noqa: BLE001
            return api_error("telegram_verify_failed", str(exc), status=400)

        if result.get("needs_password"):
            return Response({"state": "needs_password"})

        connection.set_session(result["session_string"])
        connection.bot_id = result.get("user_id", "")
        connection.bot_username = result.get("username", "")
        connection.phone_code_hash = ""
        connection.login_state = "active"
        connection.last_error = ""
        connection.save()
        return Response({"state": "active", "username": connection.bot_username})
