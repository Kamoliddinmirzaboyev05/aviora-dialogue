import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.leads.models import Lead
from apps.opportunities.models import Opportunity, ResponseDraft
from apps.workspaces.models import Workspace


pytestmark = pytest.mark.django_db


def authenticated_client():
    call_command("seed_demo")
    client = APIClient()
    login = client.post("/api/v1/auth/login/", {"email": "owner@example.com", "password": "ChangeMe123!"})
    assert login.status_code == 200
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    workspace = Workspace.objects.get(slug="demo-workspace")
    return client, workspace


def test_complete_demo_workflow_api():
    client, workspace = authenticated_client()

    simulated = client.post(
        "/api/v1/telegram/simulate-message/",
        {
            "workspace": str(workspace.id),
            "message": "Can anyone recommend a simple CRM for a small sales team?",
            "sender_name": "Alex Founder",
            "telegram_user_id": "7001",
        },
        format="json",
    )

    assert simulated.status_code == 201
    opportunity_id = simulated.data["opportunity"]["id"]
    draft_id = simulated.data["draft"]["id"]
    assert Opportunity.objects.filter(id=opportunity_id, status=Opportunity.Status.NEW).exists()
    assert ResponseDraft.objects.filter(id=draft_id, status=ResponseDraft.Status.DRAFT).exists()

    approved = client.post(f"/api/v1/approvals/{draft_id}/approve/", {}, format="json")
    assert approved.status_code == 200
    conversation_id = approved.data["conversation"]["id"]
    assert approved.data["draft"]["status"] == ResponseDraft.Status.SENT

    consent = client.post(
        f"/api/v1/conversations/{conversation_id}/simulate-consent/",
        {"message": "Yes, please send me more information."},
        format="json",
    )
    assert consent.status_code == 200
    assert consent.data["consent"]["status"] == "granted"

    product_response = client.post(f"/api/v1/conversations/{conversation_id}/generate-product-response/", {}, format="json")
    assert product_response.status_code == 200
    assert "SalesPilot CRM" in product_response.data["message"]["body"]

    lead = client.post(
        "/api/v1/leads/convert/",
        {"workspace": str(workspace.id), "conversation": conversation_id},
        format="json",
    )
    assert lead.status_code == 201
    assert Lead.objects.filter(id=lead.data["id"], status=Lead.Status.NEW).exists()

    updated = client.patch(f"/api/v1/leads/{lead.data['id']}/", {"status": Lead.Status.QUALIFIED}, format="json")
    assert updated.status_code == 200
    assert updated.data["status"] == Lead.Status.QUALIFIED

    analytics = client.get(f"/api/v1/analytics/overview/?workspace={workspace.id}")
    assert analytics.status_code == 200
    assert analytics.data["opportunities"] == 1
    assert analytics.data["consent_granted"] == 1
    assert analytics.data["leads"] == 1
