import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.opportunities.services import approve_permission_draft, simulate_incoming_message
from apps.workspaces.models import Workspace


pytestmark = pytest.mark.django_db


def login_client():
    call_command("seed_demo")
    client = APIClient()
    login = client.post("/api/v1/auth/login/", {"email": "owner@example.com", "password": "ChangeMe123!"})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    workspace = Workspace.objects.get(slug="demo-workspace")
    return client, workspace


def test_product_response_api_requires_granted_consent():
    client, workspace = login_client()
    result = simulate_incoming_message(
        workspace=workspace,
        actor=None,
        message="Can anyone recommend a simple CRM for a small sales team?",
        sender_name="Alex Founder",
        telegram_user_id="9001",
    )
    conversation = approve_permission_draft(draft=result["draft"], actor=None)

    response = client.post(f"/api/v1/conversations/{conversation.id}/generate-product-response/", {}, format="json")

    assert response.status_code == 403
    assert response.data["error"]["code"] == "consent_required"


def test_telegram_connection_api_never_returns_encrypted_bot_token():
    client, workspace = login_client()
    response = client.get(f"/api/v1/telegram/connections/?workspace={workspace.id}")

    assert response.status_code == 200
    assert "encrypted_bot_token" not in response.data["results"][0]
