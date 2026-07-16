from types import SimpleNamespace

import pytest
from django.test import override_settings

from apps.ai_engine.exceptions import AIProviderConfigurationError, AIProviderError
from apps.ai_engine.providers.gemini import GeminiAPIProvider
from apps.ai_engine.providers.mock import MockAIProvider
from apps.ai_engine.schemas import ClassificationResult, DraftResult
from apps.ai_engine.services import get_ai_provider
from apps.products.models import Product
from apps.workspaces.models import Workspace


class FakeGenAIClient:
    def __init__(self, *, parsed=None, error=None):
        self.parsed = parsed
        self.error = error
        self.models = SimpleNamespace(generate_content=self.generate_content)

    def generate_content(self, **kwargs):
        if self.error:
            raise self.error
        return SimpleNamespace(parsed=self.parsed)


@pytest.fixture
def product(db):
    workspace = Workspace.objects.create(
        name="Provider test workspace",
        business_name="Provider test business",
    )
    return Product.objects.create(
        workspace=workspace,
        name="Ethical CRM",
        short_description="A CRM for small sales teams.",
        target_customer="Small sales teams",
        problems_solved="Lead follow-up",
        benefits="Simple pipeline tracking",
        pricing_model="monthly",
        starting_price="49.00",
        website="https://example.com/ethical-crm",
    )


@override_settings(AI_PROVIDER="mock")
def test_mock_provider_needs_no_external_key():
    assert isinstance(get_ai_provider(), MockAIProvider)


@override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="")
def test_gemini_provider_reports_missing_key():
    with pytest.raises(AIProviderConfigurationError, match="GEMINI_API_KEY"):
        get_ai_provider()


@override_settings(AI_PROVIDER="unsupported")
def test_factory_rejects_unsupported_provider():
    with pytest.raises(AIProviderConfigurationError, match="Unsupported AI_PROVIDER: unsupported"):
        get_ai_provider()


def test_gemini_classification_normalizes_structured_response(product):
    client = FakeGenAIClient(
        parsed={
            "is_relevant": True,
            "intent_type": "recommendation_request",
            "confidence": 0.91,
            "detected_problem": "Needs CRM",
            "urgency": "medium",
            "language": "en",
            "sentiment": "neutral",
            "recommended_action": "draft_permission_request",
            "concise_reason": "CRM request",
            "risk_flags": [],
        }
    )

    result = GeminiAPIProvider(api_key="test-key", model="gemini-2.5-flash", client=client).classify_message(
        message="Recommend a CRM",
        product=product,
        consent_status="unknown",
    )

    assert result == ClassificationResult(
        is_relevant=True,
        intent_type="recommendation_request",
        confidence=0.91,
        detected_problem="Needs CRM",
        urgency="medium",
        language="en",
        sentiment="neutral",
        recommended_action="draft_permission_request",
        concise_reason="CRM request",
        risk_flags=[],
    )


def test_gemini_permission_request_normalizes_structured_response():
    client = FakeGenAIClient(
        parsed={
            "text": "May I send you a relevant suggestion?",
            "concise_reason": "Permission-first response",
            "safety_flags": [],
        }
    )

    result = GeminiAPIProvider(api_key="test-key", model="gemini-2.5-flash", client=client).generate_permission_request(
        message="Recommend a CRM"
    )

    assert result == DraftResult(
        text="May I send you a relevant suggestion?",
        concise_reason="Permission-first response",
        safety_flags=[],
    )


def test_gemini_provider_sanitizes_upstream_failures(product):
    client = FakeGenAIClient(error=RuntimeError("credential=secret-token"))
    provider = GeminiAPIProvider(api_key="test-key", model="gemini-2.5-flash", client=client)

    with pytest.raises(AIProviderError, match="Gemini request failed") as error:
        provider.generate_product_response(
            message="Recommend a CRM",
            product=product,
            consent_status="granted",
        )

    assert "secret-token" not in str(error.value)
