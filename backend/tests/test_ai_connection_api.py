import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient

from apps.ai_engine.exceptions import AIProviderError
from apps.ai_engine.providers.mock import MockAIProvider
from apps.products.models import Product
from apps.workspaces.models import Workspace, WorkspaceMembership


pytestmark = pytest.mark.django_db


@pytest.fixture
def workspace():
    return Workspace.objects.create(name="AI connection workspace", business_name="Ethical CRM")


@pytest.fixture
def product(workspace):
    return Product.objects.create(
        workspace=workspace,
        name="Ethical CRM",
        short_description="A CRM for small sales teams.",
        status="active",
    )


@pytest.fixture
def owner_client(workspace):
    user = get_user_model().objects.create_user(email="owner@example.com", password="ChangeMe123!")
    WorkspaceMembership.objects.create(user=user, workspace=workspace, role=WorkspaceMembership.Role.OWNER)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def reviewer_client(workspace):
    user = get_user_model().objects.create_user(email="reviewer@example.com", password="ChangeMe123!")
    WorkspaceMembership.objects.create(user=user, workspace=workspace, role=WorkspaceMembership.Role.REVIEWER)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_workspace_owner_can_test_ai_connection(owner_client, workspace, product, monkeypatch):
    monkeypatch.setattr("apps.ai_engine.views.get_ai_provider", lambda: MockAIProvider())

    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")

    assert response.status_code == 200
    assert response.data["provider"] == "mock"
    assert response.data["model"] == "mock"
    assert response.data["state"] == "connected"
    assert isinstance(response.data["latency_ms"], int)
    assert response.data["classification"]["intent_type"] == "recommendation_request"


def test_workspace_reviewer_cannot_test_ai_connection(reviewer_client, workspace):
    response = reviewer_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")

    assert response.status_code == 403


def test_ai_connection_hides_provider_error_details(owner_client, workspace, product, monkeypatch):
    secret_sentinel = "provider-secret-sentinel"
    monkeypatch.setattr(
        "apps.ai_engine.views.get_ai_provider",
        lambda: (_ for _ in ()).throw(AIProviderError(secret_sentinel)),
    )

    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")

    assert response.status_code == 503
    assert response.data["error"]["code"] == "ai_connection_failed"
    assert response.data["error"]["message"] == "AI provider connection test failed."
    assert secret_sentinel not in str(response.data)


def test_ai_connection_rejects_malformed_workspace_id(owner_client):
    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": "not-a-uuid"}, format="json")

    assert response.status_code == 400
    assert response.data["error"]["code"] == "invalid_workspace"


def test_ai_connection_denies_inactive_workspace(owner_client, workspace, product):
    workspace.is_active = False
    workspace.save(update_fields=["is_active"])

    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")

    assert response.status_code == 403
    assert response.data["error"]["code"] == "workspace_admin_required"


@override_settings(AI_PROVIDER="vertex", VERTEX_PROJECT_ID="", VERTEX_LOCATION="", VERTEX_MODEL="")
def test_ai_connection_returns_sanitized_error_for_vertex_configuration(owner_client, workspace, product):
    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")

    assert response.status_code == 503
    assert response.data["error"]["code"] == "ai_connection_failed"
    assert response.data["error"]["message"] == "AI provider connection test failed."
