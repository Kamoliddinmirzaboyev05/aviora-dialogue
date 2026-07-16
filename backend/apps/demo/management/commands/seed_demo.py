from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.billing.models import Plan, Subscription
from apps.products.models import Product
from apps.telegram_integration.models import TelegramChat, TelegramConnection
from apps.triggers.models import TriggerSet
from apps.workspaces.models import Workspace, WorkspaceMembership


class Command(BaseCommand):
    help = "Create deterministic demo data for local development."

    def handle(self, *args, **options):
        user_model = get_user_model()
        owner, _ = user_model.objects.get_or_create(
            email="owner@example.com",
            defaults={"full_name": "Demo Owner", "username": "owner@example.com"},
        )
        owner.set_password("ChangeMe123!")
        owner.save(update_fields=["password"])

        manager, _ = user_model.objects.get_or_create(
            email="manager@example.com",
            defaults={"full_name": "Demo Manager", "username": "manager@example.com"},
        )
        manager.set_password("ChangeMe123!")
        manager.save(update_fields=["password"])

        workspace, _ = Workspace.objects.get_or_create(
            slug="demo-workspace",
            defaults={
                "name": "Demo Workspace",
                "business_name": "Ethical Dialogue AI Demo",
                "industry": "SaaS",
                "default_language": "en",
            },
        )
        WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=owner,
            defaults={"role": WorkspaceMembership.Role.OWNER},
        )
        WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=manager,
            defaults={"role": WorkspaceMembership.Role.MANAGER},
        )

        product, _ = Product.objects.get_or_create(
            workspace=workspace,
            name="SalesPilot CRM",
            defaults={
                "short_description": "A simple CRM for small sales teams that need clean follow-up tracking.",
                "target_customer": "Small sales teams",
                "problems_solved": "Lost follow-ups, scattered lead notes, and unclear pipeline ownership.",
                "benefits": "Easy pipeline tracking, reminders, manager handoff, and lightweight reporting.",
                "pricing_model": "per seat",
                "starting_price": "19.00",
                "currency": "USD",
                "website": "https://example.com/salespilot",
                "booking_link": "https://example.com/book-demo",
            },
        )
        TriggerSet.objects.get_or_create(
            workspace=workspace,
            name="CRM recommendation intent",
            defaults={
                "description": "Detects requests for CRM recommendations from small teams.",
                "product": product,
                "positive_keywords": ["crm", "sales team", "recommend", "pipeline", "lead tracking"],
                "negative_keywords": ["job", "hiring", "coursework"],
                "positive_examples": ["Can anyone recommend a simple CRM for a small sales team?"],
                "negative_examples": ["I need a job as a CRM administrator."],
            },
        )
        connection, _ = TelegramConnection.objects.get_or_create(
            workspace=workspace,
            provider="mock",
            defaults={
                "name": "Mock Telegram",
                "bot_username": "ethical_dialogue_demo_bot",
                "bot_id": "10001",
                "webhook_status": "mock_active",
            },
        )
        TelegramChat.objects.get_or_create(
            workspace=workspace,
            telegram_chat_id="-100100200300",
            defaults={
                "connection": connection,
                "title": "Small Business Sales Community",
                "chat_type": "group",
                "reply_mode": "approval",
            },
        )
        plan, _ = Plan.objects.get_or_create(
            name="Growth",
            defaults={"monthly_price": "49.00", "limits": {"monthly_ai_requests": 5000, "monitored_chats": 10}},
        )
        Subscription.objects.get_or_create(workspace=workspace, defaults={"plan": plan})

        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: owner@example.com / ChangeMe123!"))
