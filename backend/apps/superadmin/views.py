from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import CharField, Count, F, OuterRef, Q, Subquery, Value
from django.db.models.functions import Concat
from rest_framework import serializers
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_engine.models import AIRequestLog
from apps.audit_logs.models import AuditLog
from apps.billing.models import Subscription
from apps.consent.models import ConsentRecord
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.superadmin.permissions import IsPlatformStaff
from apps.telegram_integration.models import TelegramConnection
from apps.workspaces.models import Workspace, WorkspaceMembership


class WorkspaceOverviewSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    business_name = serializers.CharField()
    industry = serializers.CharField()
    is_active = serializers.BooleanField()
    owner = serializers.CharField(allow_null=True)
    member_count = serializers.IntegerField()
    lead_count = serializers.IntegerField()
    plan = serializers.CharField(allow_null=True)


class UserOverviewSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    membership_count = serializers.IntegerField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    last_login = serializers.DateTimeField(allow_null=True)


class PlatformOverviewView(APIView):
    permission_classes = [IsPlatformStaff]

    def get(self, request):
        return Response(
            {
                "users": get_user_model().objects.count(),
                "active_workspaces": Workspace.objects.filter(is_active=True).count(),
                "opportunities": Opportunity.objects.count(),
                "consent_grants": ConsentRecord.objects.filter(
                    status=ConsentRecord.Status.GRANTED
                ).count(),
                "leads": Lead.objects.count(),
                "telegram_connections": TelegramConnection.objects.filter(
                    is_active=True
                ).count(),
            }
        )


class WorkspaceListView(ListAPIView):
    serializer_class = WorkspaceOverviewSerializer
    permission_classes = [IsPlatformStaff]

    def get_queryset(self):
        owner_email = Subquery(
            WorkspaceMembership.objects.filter(
                workspace=OuterRef("pk"),
                role=WorkspaceMembership.Role.OWNER,
                is_active=True,
            )
            .order_by("created_at")
            .values("user__email")[:1]
        )
        plan_name = Subquery(
            Subscription.objects.filter(workspace=OuterRef("pk"))
            .order_by("-created_at")
            .values("plan__name")[:1]
        )
        queryset = Workspace.objects.annotate(
            owner=owner_email,
            member_count=Count(
                "memberships",
                filter=Q(memberships__is_active=True),
                distinct=True,
            ),
            lead_count=Count("lead", distinct=True),
            plan=plan_name,
        )
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(business_name__icontains=search)
                | Q(slug__icontains=search)
                | Q(industry__icontains=search)
                | Q(owner__icontains=search)
            )
        return queryset.order_by("name", "id")


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(required=False, allow_blank=True, default="")
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["admin", "superadmin"], default="admin")

    def validate_email(self, value):
        value = value.strip().lower()
        model = get_user_model()
        if model.objects.filter(Q(email__iexact=value) | Q(username__iexact=value)).exists():
            raise serializers.ValidationError("Bu email allaqachon mavjud.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_role(self, value):
        # Only a superuser may mint another superadmin (privilege escalation guard).
        if value == "superadmin" and not self.context["request"].user.is_superuser:
            raise serializers.ValidationError("Superadmin yaratish uchun superuser huquqi kerak.")
        return value

    def create(self, validated_data):
        role = validated_data["role"]
        return get_user_model().objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            is_staff=True,
            is_superuser=(role == "superadmin"),
        )

    def to_representation(self, instance):
        return {
            "id": str(instance.pk),
            "email": instance.email,
            "full_name": instance.full_name,
            "is_staff": instance.is_staff,
            "is_superuser": instance.is_superuser,
        }


class UserListView(ListCreateAPIView):
    permission_classes = [IsPlatformStaff]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserOverviewSerializer

    def get_queryset(self):
        queryset = get_user_model().objects.annotate(
            membership_count=Count(
                "workspace_memberships",
                filter=Q(workspace_memberships__is_active=True),
                distinct=True,
            )
        )
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(full_name__icontains=search)
            )
        return queryset.order_by("email", "id")


class IntegrationStatusView(APIView):
    permission_classes = [IsPlatformStaff]

    def get(self, request):
        ai_model = (
            settings.VERTEX_MODEL
            if settings.AI_PROVIDER == "vertex"
            else settings.GEMINI_MODEL
        )
        return Response(
            {
                "ai": {
                    "provider": settings.AI_PROVIDER,
                    "model": ai_model,
                    "credential_configured": _ai_credential_configured(),
                    "vertex_project_configured": bool(settings.VERTEX_PROJECT_ID),
                },
                "telegram": {
                    "provider": settings.TELEGRAM_PROVIDER,
                    "bot_token_configured": bool(settings.TELEGRAM_BOT_TOKEN),
                    "webhook_secret_configured": bool(settings.TELEGRAM_WEBHOOK_SECRET),
                    "webhook_base_url_configured": bool(settings.TELEGRAM_WEBHOOK_BASE_URL),
                },
            }
        )


class RecentEventsView(APIView):
    permission_classes = [IsPlatformStaff]
    pagination_class = PageNumberPagination

    def get(self, request):
        ai_failures = AIRequestLog.objects.filter(succeeded=False).annotate(
            source=Value("ai_request_failure", output_field=CharField()),
            workspace_name=F("workspace__name"),
            event_at=F("created_at"),
            event_summary=Concat(
                Value("AI "), F("purpose"), Value(" so'rovi bajarilmadi."), output_field=CharField()
            ),
        ).values("id", "source", "workspace_name", "event_at", "event_summary")
        telegram_errors = TelegramConnection.objects.exclude(last_error="").annotate(
            source=Value("telegram_connection_error", output_field=CharField()),
            workspace_name=F("workspace__name"),
            event_at=F("updated_at"),
            event_summary=Value(
                "Telegram ulanishida qayd etilgan xatolik bor.", output_field=CharField()
            ),
        ).values("id", "source", "workspace_name", "event_at", "event_summary")
        audit_events = AuditLog.objects.annotate(
            source=Value("audit_log", output_field=CharField()),
            workspace_name=F("workspace__name"),
            event_at=F("created_at"),
            event_summary=Concat(
                F("action"),
                Value(" ("),
                F("resource_type"),
                Value(")"),
                output_field=CharField(),
            ),
        ).values("id", "source", "workspace_name", "event_at", "event_summary")
        events = ai_failures.union(telegram_errors, audit_events, all=True).order_by("-event_at")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(events, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(_serialize_events(page))
        return Response(_serialize_events(events))


def _serialize_events(events):
    return [
        {
            "id": str(event["id"]),
            "source": event["source"],
            "workspace": event["workspace_name"],
            "created_at": event["event_at"],
            "summary": event["event_summary"],
        }
        for event in events
    ]


def _ai_credential_configured():
    if settings.AI_PROVIDER == "mock":
        return True
    if settings.AI_PROVIDER == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if settings.AI_PROVIDER == "vertex":
        return all(
            [
                settings.VERTEX_PROJECT_ID,
                settings.VERTEX_LOCATION,
                settings.VERTEX_MODEL,
            ]
        )
    return False
