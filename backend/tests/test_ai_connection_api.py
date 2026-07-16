import pytest
from django.contrib.auth import get_user_model
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


def test_ai_connection_returns_sanitized_provider_error(owner_client, workspace, product, monkeypatch):
    monkeypatch.setattr(
        "apps.ai_engine.views.get_ai_provider",
        lambda: (_ for _ in ()).throw(AIProviderError("AI provider is unavailable.")),
    )

    response = owner_client.post("/api/v1/ai/test-connection/", {"workspace": str(workspace.id)}, format="json")

    assert response.status_code == 503
    assert response.data["error"]["code"] == "ai_connection_failed"
    assert response.data["error"]["message"] == "AI provider is unavailable."
