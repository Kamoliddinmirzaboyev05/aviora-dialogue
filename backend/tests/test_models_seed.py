import pytest
from django.core.management import call_command

from apps.products.models import Product
from apps.telegram_integration.models import TelegramChat, TelegramConnection
from apps.triggers.models import TriggerSet
from apps.workspaces.models import Workspace


pytestmark = pytest.mark.django_db


def test_seed_demo_creates_idempotent_workspace_and_demo_assets():
    call_command("seed_demo")
    call_command("seed_demo")

    assert Workspace.objects.filter(slug="demo-workspace").count() == 1
    workspace = Workspace.objects.get(slug="demo-workspace")
    assert Product.objects.filter(workspace=workspace, name="SalesPilot CRM").count() == 1
    assert TriggerSet.objects.filter(workspace=workspace, name="CRM recommendation intent").count() == 1
    assert TelegramConnection.objects.filter(workspace=workspace, provider="mock").count() == 1
    assert TelegramChat.objects.filter(workspace=workspace, title="Small Business Sales Community").count() == 1
