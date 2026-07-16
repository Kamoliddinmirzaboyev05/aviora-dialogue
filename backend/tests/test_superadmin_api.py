import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.ai_engine.models import AIRequestLog
from apps.audit_logs.models import AuditLog
from apps.billing.models import Plan, Subscription
from apps.consent.models import ConsentRecord
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.telegram_integration.models import (
    TelegramChat,
    TelegramConnection,
    TelegramContact,
)
from apps.workspaces.models import Workspace, WorkspaceMembership


pytestmark = pytest.mark.django_db


@pytest.fixture
def user_client():
    user = get_user_model().objects.create_user(
        email="member@example.com", password="ChangeMe123!"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def staff_client():
    user = get_user_model().objects.create_user(
        email="staff@example.com", password="ChangeMe123!", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def platform_data():
    owner = get_user_model().objects.create_user(
        email="owner@example.com", password="ChangeMe123!", full_name="Workspace Owner"
    )
    workspace = Workspace.objects.create(
        name="Northwind Sales", business_name="Northwind Traders", industry="Retail"
    )
    WorkspaceMembership.objects.create(
        user=owner, workspace=workspace, role=WorkspaceMembership.Role.OWNER
    )
    plan = Plan.objects.create(name="Growth")
    Subscription.objects.create(workspace=workspace, plan=plan)
    connection = TelegramConnection.objects.create(
        workspace=workspace,
        name="Northwind Telegram",
        provider="bot_api",
        is_active=True,
        webhook_status="error",
        last_error="Telegram delivery failed.",
    )
    contact = TelegramContact.objects.create(
        workspace=workspace, telegram_user_id="northwind-contact", display_name="Prospective Buyer"
    )
    chat = TelegramChat.objects.create(
        workspace=workspace,
        connection=connection,
        title="Northwind group",
        telegram_chat_id="northwind-chat",
    )
    Opportunity.objects.create(
        workspace=workspace,
        chat=chat,
        contact=contact,
        source_message="I need a better CRM.",
        detected_intent="recommendation_request",
    )
    ConsentRecord.objects.create(
        workspace=workspace, contact=contact, status=ConsentRecord.Status.GRANTED
    )
    Lead.objects.create(
        workspace=workspace, contact=contact, detected_need="CRM", score=90
    )
    AIRequestLog.objects.create(
        workspace=workspace,
        provider="gemini",
        model="gemini-2.5-flash",
        purpose="classify_message",
        succeeded=False,
        concise_reason="Provider request failed.",
    )
    AuditLog.objects.create(
        workspace=workspace,
        actor=owner,
        action="lead.created",
        resource_type="lead",
        summary="Created qualified lead.",
    )
    return {"owner": owner, "workspace": workspace}


@pytest.mark.parametrize(
    "route",
    [
        "/api/v1/superadmin/overview/",
        "/api/v1/superadmin/workspaces/",
        "/api/v1/superadmin/users/",
        "/api/v1/superadmin/integrations/",
        "/api/v1/superadmin/events/",
    ],
)
def test_regular_user_cannot_access_superadmin(user_client, route):
    assert user_client.get(route).status_code == 403


def test_staff_user_sees_platform_overview(staff_client, platform_data):
    response = staff_client.get("/api/v1/superadmin/overview/")

    assert response.status_code == 200
    assert set(response.data) >= {
        "users",
        "active_workspaces",
        "opportunities",
        "consent_grants",
        "leads",
        "telegram_connections",
    }
    assert response.data["active_workspaces"] == 1
    assert response.data["opportunities"] == 1
    assert response.data["consent_grants"] == 1
    assert response.data["leads"] == 1
    assert response.data["telegram_connections"] == 1


def test_integrations_return_presence_not_secrets(staff_client, settings):
    settings.AI_PROVIDER = "gemini"
    settings.GEMINI_API_KEY = "never-return-me"
    settings.TELEGRAM_BOT_TOKEN = "telegram-token-never-return-me"
    settings.TELEGRAM_WEBHOOK_SECRET = "webhook-secret-never-return-me"

    response = staff_client.get("/api/v1/superadmin/integrations/")

    assert response.status_code == 200
    assert response.data["ai"]["credential_configured"] is True
    assert response.data["telegram"]["bot_token_configured"] is True
    assert response.data["telegram"]["webhook_secret_configured"] is True
    assert "never-return-me" not in str(response.data)


@pytest.mark.parametrize(
    ("provider", "gemini_key", "vertex_project", "vertex_location", "vertex_model", "expected"),
    [
        ("mock", "", "", "", "", True),
        ("gemini", "", "", "", "", False),
        ("gemini", "configured-gemini-key", "", "", "", True),
        ("vertex", "", "project-123", "", "gemini-2.5-flash", False),
        ("vertex", "", "project-123", "us-central1", "gemini-2.5-flash", True),
        ("unknown", "configured-gemini-key", "", "", "", False),
    ],
)
def test_ai_credential_status_reflects_selected_provider(
    staff_client,
    settings,
    provider,
    gemini_key,
    vertex_project,
    vertex_location,
    vertex_model,
    expected,
):
    settings.AI_PROVIDER = provider
    settings.GEMINI_API_KEY = gemini_key
    settings.VERTEX_PROJECT_ID = vertex_project
    settings.VERTEX_LOCATION = vertex_location
    settings.VERTEX_MODEL = vertex_model

    response = staff_client.get("/api/v1/superadmin/integrations/")

    assert response.status_code == 200
    assert response.data["ai"]["credential_configured"] is expected
    assert "configured-gemini-key" not in str(response.data)


def test_me_includes_staff_identity_flags(staff_client):
    response = staff_client.get("/api/v1/auth/me/")

    assert response.status_code == 200
    assert response.data["user"]["is_staff"] is True
    assert response.data["user"]["is_superuser"] is False


def test_staff_can_search_paginated_workspace_rows(staff_client, platform_data):
    response = staff_client.get("/api/v1/superadmin/workspaces/?search=Northwind")

    assert response.status_code == 200
    assert response.data["count"] == 1
    row = response.data["results"][0]
    assert row == {
        "id": str(platform_data["workspace"].id),
        "name": "Northwind Sales",
        "business_name": "Northwind Traders",
        "industry": "Retail",
        "is_active": True,
        "owner": "owner@example.com",
        "member_count": 1,
        "lead_count": 1,
        "plan": "Growth",
    }


def test_workspace_list_hides_offboarded_owner_from_display_and_search(
    staff_client, platform_data
):
    WorkspaceMembership.objects.filter(
        workspace=platform_data["workspace"],
        user=platform_data["owner"],
        role=WorkspaceMembership.Role.OWNER,
    ).update(is_active=False)

    workspace_response = staff_client.get("/api/v1/superadmin/workspaces/?search=Northwind")
    owner_search_response = staff_client.get(
        "/api/v1/superadmin/workspaces/?search=owner@example.com"
    )

    assert workspace_response.status_code == 200
    assert workspace_response.data["results"][0]["owner"] is None
    assert owner_search_response.status_code == 200
    assert owner_search_response.data["count"] == 0


def test_staff_can_search_paginated_user_rows(staff_client, platform_data):
    response = staff_client.get("/api/v1/superadmin/users/?search=Workspace%20Owner")

    assert response.status_code == 200
    assert response.data["count"] == 1
    row = response.data["results"][0]
    assert row["id"] == str(platform_data["owner"].id)
    assert row["email"] == "owner@example.com"
    assert row["full_name"] == "Workspace Owner"
    assert row["membership_count"] == 1
    assert row["is_staff"] is False
    assert row["is_superuser"] is False
    assert row["last_login"] is None


def test_staff_can_view_recent_operational_events(staff_client, platform_data):
    response = staff_client.get("/api/v1/superadmin/events/")

    assert response.status_code == 200
    assert response.data["count"] == 3
    assert {event["source"] for event in response.data["results"]} == {
        "ai_request_failure",
        "telegram_connection_error",
        "audit_log",
    }
    assert all(event["workspace"] == "Northwind Sales" for event in response.data["results"])
