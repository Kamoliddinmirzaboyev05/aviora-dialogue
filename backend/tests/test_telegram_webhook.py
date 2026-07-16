from copy import deepcopy
from uuid import UUID

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.opportunities.models import Opportunity
from apps.products.models import Product
from apps.telegram_integration.exceptions import TelegramProviderError
from apps.telegram_integration.models import (
    TelegramChat,
    TelegramConnection,
    TelegramContact,
    TelegramUpdate,
)
from apps.triggers.models import TriggerSet
from apps.workspaces.models import Workspace, WorkspaceMembership


pytestmark = pytest.mark.django_db

TELEGRAM_UPDATE = {
    "update_id": 10001,
    "message": {
        "message_id": 77,
        "from": {
            "id": 7001,
            "is_bot": False,
            "first_name": "Ada",
            "last_name": "Lovelace",
            "username": "ada",
        },
        "chat": {"id": -100100200300, "title": "CRM Community", "type": "group"},
        "text": "Can anyone recommend a simple CRM for a small sales team?",
    },
}


@pytest.fixture
def workspace():
    return Workspace.objects.create(
        name="Telegram workspace", business_name="Ethical CRM"
    )


@pytest.fixture
def connection(workspace):
    return TelegramConnection.objects.create(
        workspace=workspace,
        name="Telegram Bot",
        provider="mock",
        is_active=True,
    )


@pytest.fixture
def chat(workspace, connection):
    return TelegramChat.objects.create(
        workspace=workspace,
        connection=connection,
        title="CRM Community",
        telegram_chat_id="-100100200300",
        monitoring_enabled=True,
        admin_approved=True,
    )


@pytest.fixture
def workflow(workspace, chat):
    product = Product.objects.create(
        workspace=workspace,
        name="Ethical CRM",
        short_description="A CRM for small sales teams.",
        status="active",
    )
    TriggerSet.objects.create(
        workspace=workspace,
        name="CRM recommendation",
        product=product,
        enabled=True,
        positive_keywords=["crm", "recommend", "sales team"],
        minimum_score=50,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner_client(workspace):
    user = get_user_model().objects.create_user(
        email="owner@example.com", password="ChangeMe123!"
    )
    WorkspaceMembership.objects.create(
        user=user, workspace=workspace, role=WorkspaceMembership.Role.OWNER
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def reviewer_client(workspace):
    user = get_user_model().objects.create_user(
        email="reviewer@example.com", password="ChangeMe123!"
    )
    WorkspaceMembership.objects.create(
        user=user, workspace=workspace, role=WorkspaceMembership.Role.REVIEWER
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def webhook_url(connection):
    return f"/api/v1/telegram/webhook/{connection.id}/"


def post_update(api_client, connection, payload=TELEGRAM_UPDATE, secret="expected"):
    return api_client.post(
        webhook_url(connection),
        payload,
        format="json",
        HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=secret,
    )


def test_webhook_rejects_wrong_secret(api_client, connection, settings):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"

    response = post_update(api_client, connection, secret="wrong")

    assert response.status_code == 403
    assert response.data["error"]["code"] == "invalid_webhook_secret"
    assert TelegramUpdate.objects.count() == 0


def test_webhook_rejects_requests_when_secret_is_not_configured(
    api_client, connection, settings
):
    settings.TELEGRAM_WEBHOOK_SECRET = ""

    response = post_update(api_client, connection, secret="")

    assert response.status_code == 403
    assert TelegramUpdate.objects.count() == 0


def test_webhook_is_idempotent_and_runs_workflow_once(
    api_client, connection, chat, workflow, settings
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"

    first = post_update(api_client, connection)
    second = post_update(api_client, connection)

    assert first.status_code == second.status_code == 200
    assert (
        TelegramUpdate.objects.filter(connection=connection, update_id="10001").count()
        == 1
    )
    assert (
        Opportunity.objects.filter(workspace=connection.workspace, chat=chat).count()
        == 1
    )
    contact = TelegramContact.objects.get(
        workspace=connection.workspace, telegram_user_id="7001"
    )
    assert contact.display_name == "Ada Lovelace"


def test_webhook_routes_bot_api_update_to_exact_validated_chat(
    api_client, connection, chat, workflow, settings
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    connection.provider = "bot_api"
    connection.save(update_fields=["provider"])
    wrong_chat = TelegramChat.objects.create(
        id=UUID(int=0),
        workspace=connection.workspace,
        connection=connection,
        title="Wrong unapproved chat",
        telegram_chat_id="-999",
        monitoring_enabled=True,
        admin_approved=False,
    )
    api_client.raise_request_exception = False

    response = post_update(api_client, connection)

    assert response.status_code == 200
    opportunity = Opportunity.objects.get(workspace=connection.workspace)
    assert opportunity.chat == chat
    assert opportunity.chat != wrong_chat


def test_webhook_retries_failed_update_and_marks_it_processed(
    api_client, connection, chat, settings, monkeypatch
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    attempts = 0

    def flaky_workflow(**_kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary workflow failure")
        return {"opportunity": None, "draft": None}

    monkeypatch.setattr(
        "apps.opportunities.services.simulate_incoming_message", flaky_workflow
    )
    api_client.raise_request_exception = False

    first = post_update(api_client, connection)

    assert first.status_code == 500
    update = TelegramUpdate.objects.get(connection=connection, update_id="10001")
    assert update.status == "failed"

    second = post_update(api_client, connection)

    assert second.status_code == 200
    update.refresh_from_db()
    assert update.status == "processed"
    assert attempts == 2
    assert (
        TelegramUpdate.objects.filter(connection=connection, update_id="10001").count()
        == 1
    )


def test_webhook_does_not_process_duplicate_while_update_is_processing(
    api_client, connection, chat, settings, monkeypatch
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    TelegramUpdate.objects.create(
        workspace=connection.workspace,
        connection=connection,
        update_id="10001",
        payload=TELEGRAM_UPDATE,
        status="processing",
    )
    workflow_calls = 0

    def unexpected_workflow(**_kwargs):
        nonlocal workflow_calls
        workflow_calls += 1
        return {"opportunity": None, "draft": None}

    monkeypatch.setattr(
        "apps.opportunities.services.simulate_incoming_message", unexpected_workflow
    )

    response = post_update(api_client, connection)

    assert response.status_code == 200
    assert workflow_calls == 0
    assert Opportunity.objects.count() == 0
    update = TelegramUpdate.objects.get(connection=connection, update_id="10001")
    assert update.status == "processing"


def test_webhook_rolls_back_workflow_effects_before_marking_update_failed(
    api_client, connection, chat, workflow, settings, monkeypatch
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"

    def failing_workflow(
        *, workspace, chat, message, sender_name, telegram_user_id, **_kwargs
    ):
        contact = TelegramContact.objects.create(
            workspace=workspace,
            telegram_user_id=telegram_user_id,
            display_name=sender_name,
        )
        Opportunity.objects.create(
            workspace=workspace,
            chat=chat,
            contact=contact,
            product=Product.objects.get(workspace=workspace),
            trigger_set=TriggerSet.objects.get(workspace=workspace),
            source_message=message,
            detected_intent="test",
        )
        raise RuntimeError("temporary workflow failure")

    monkeypatch.setattr(
        "apps.opportunities.services.simulate_incoming_message", failing_workflow
    )
    api_client.raise_request_exception = False

    response = post_update(api_client, connection)

    assert response.status_code == 500
    assert Opportunity.objects.count() == 0
    assert TelegramContact.objects.count() == 0
    update = TelegramUpdate.objects.get(connection=connection, update_id="10001")
    assert update.status == "failed"


@pytest.mark.parametrize("field", ["monitoring_enabled", "admin_approved"])
def test_webhook_does_not_run_workflow_for_unmonitored_or_unapproved_chat(
    api_client, connection, chat, workflow, settings, field
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    setattr(chat, field, False)
    chat.save(update_fields=[field])

    response = post_update(api_client, connection)

    assert response.status_code == 200
    assert (
        TelegramUpdate.objects.get(connection=connection, update_id="10001").status
        == "ignored"
    )
    assert Opportunity.objects.count() == 0


def test_webhook_does_not_run_workflow_for_inactive_connection(
    api_client, connection, chat, workflow, settings
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    connection.is_active = False
    connection.save(update_fields=["is_active"])

    response = post_update(api_client, connection)

    assert response.status_code == 200
    assert (
        TelegramUpdate.objects.get(connection=connection, update_id="10001").status
        == "ignored"
    )
    assert Opportunity.objects.count() == 0


def test_webhook_acknowledges_and_persists_unsupported_update(
    api_client, connection, settings
):
    settings.TELEGRAM_WEBHOOK_SECRET = "expected"
    unsupported = {
        "update_id": 10002,
        "edited_message": deepcopy(TELEGRAM_UPDATE["message"]),
    }

    response = post_update(api_client, connection, payload=unsupported)

    assert response.status_code == 200
    assert (
        TelegramUpdate.objects.get(connection=connection, update_id="10002").status
        == "unsupported"
    )
    assert Opportunity.objects.count() == 0


class FakeTelegramProvider:
    def __init__(self, *, error=None):
        self.error = error
        self.webhooks = []

    def get_me(self):
        if self.error:
            raise self.error
        return {"id": 123456, "username": "ethical_bot", "first_name": "Ethical Bot"}

    def set_webhook(self, *, url, secret_token):
        if self.error:
            raise self.error
        self.webhooks.append((url, secret_token))
        return True


def test_workspace_owner_can_test_telegram_connection(
    owner_client, workspace, monkeypatch
):
    monkeypatch.setattr(
        "apps.telegram_integration.views.get_telegram_provider",
        lambda: FakeTelegramProvider(),
    )

    response = owner_client.post(
        "/api/v1/telegram/test-connection/",
        {"workspace": str(workspace.id)},
        format="json",
    )

    assert response.status_code == 200
    assert response.data == {
        "state": "connected",
        "bot": {"id": "123456", "username": "ethical_bot"},
    }


def test_workspace_owner_can_test_mock_telegram_connection(
    owner_client, workspace, settings
):
    settings.TELEGRAM_PROVIDER = "mock"
    owner_client.raise_request_exception = False

    response = owner_client.post(
        "/api/v1/telegram/test-connection/",
        {"workspace": str(workspace.id)},
        format="json",
    )

    assert response.status_code == 200
    assert response.data == {
        "state": "connected",
        "bot": {"id": "mock-bot", "username": "mock_telegram_bot"},
    }


def test_workspace_reviewer_cannot_test_telegram_connection(reviewer_client, workspace):
    response = reviewer_client.post(
        "/api/v1/telegram/test-connection/",
        {"workspace": str(workspace.id)},
        format="json",
    )

    assert response.status_code == 403


def test_workspace_owner_can_register_webhook(
    owner_client, workspace, connection, settings, monkeypatch
):
    settings.TELEGRAM_WEBHOOK_SECRET = "registration-secret"
    settings.TELEGRAM_WEBHOOK_BASE_URL = "https://app.example.com"
    provider = FakeTelegramProvider()
    monkeypatch.setattr(
        "apps.telegram_integration.views.get_telegram_provider", lambda: provider
    )

    response = owner_client.post(
        "/api/v1/telegram/register-webhook/",
        {"workspace": str(workspace.id), "connection": str(connection.id)},
        format="json",
    )

    expected_url = f"https://app.example.com/api/v1/telegram/webhook/{connection.id}/"
    assert response.status_code == 200
    assert response.data == {"state": "registered", "webhook_url": expected_url}
    assert "registration-secret" not in str(response.data)
    assert provider.webhooks == [(expected_url, "registration-secret")]
    connection.refresh_from_db()
    assert connection.webhook_url == expected_url
    assert connection.webhook_status == "active"


def test_workspace_owner_can_register_mock_webhook(
    owner_client, workspace, connection, settings
):
    settings.TELEGRAM_PROVIDER = "mock"
    settings.TELEGRAM_WEBHOOK_SECRET = "mock-registration-secret"
    settings.TELEGRAM_WEBHOOK_BASE_URL = "https://app.example.com"
    owner_client.raise_request_exception = False

    response = owner_client.post(
        "/api/v1/telegram/register-webhook/",
        {"workspace": str(workspace.id), "connection": str(connection.id)},
        format="json",
    )

    expected_url = f"https://app.example.com/api/v1/telegram/webhook/{connection.id}/"
    assert response.status_code == 200
    assert response.data == {"state": "registered", "webhook_url": expected_url}
    assert "mock-registration-secret" not in str(response.data)
    connection.refresh_from_db()
    assert connection.webhook_status == "active"


def test_telegram_management_error_is_sanitized(owner_client, workspace, monkeypatch):
    secret = "provider-secret-sentinel"
    monkeypatch.setattr(
        "apps.telegram_integration.views.get_telegram_provider",
        lambda: FakeTelegramProvider(error=TelegramProviderError(secret)),
    )

    response = owner_client.post(
        "/api/v1/telegram/test-connection/",
        {"workspace": str(workspace.id)},
        format="json",
    )

    assert response.status_code == 503
    assert response.data["error"] == {
        "code": "telegram_connection_failed",
        "message": "Telegram provider connection test failed.",
        "fields": {},
    }
    assert secret not in str(response.data)
