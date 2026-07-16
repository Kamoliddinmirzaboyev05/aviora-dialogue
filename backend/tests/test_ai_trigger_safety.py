import pytest
from django.core.management import call_command

from apps.ai_engine.services import get_ai_provider
from apps.ai_engine.safety import validate_permission_first_response, validate_product_response
from apps.consent.models import ConsentRecord
from apps.products.models import Product
from apps.triggers.models import TriggerSet
from apps.triggers.services import match_trigger_set
from apps.workspaces.models import Workspace


pytestmark = pytest.mark.django_db


def test_trigger_matching_scores_crm_recommendation_and_excludes_negative_context():
    call_command("seed_demo")
    workspace = Workspace.objects.get(slug="demo-workspace")
    trigger = TriggerSet.objects.get(workspace=workspace)

    positive = match_trigger_set("Can anyone recommend a simple CRM for a small sales team?", trigger)
    negative = match_trigger_set("I need a job as a CRM administrator.", trigger)

    assert positive.is_match is True
    assert positive.score >= trigger.minimum_score
    assert "crm" in positive.matched_positive_terms
    assert negative.is_match is False
    assert "job" in negative.matched_negative_terms


def test_mock_ai_generates_permission_first_draft_and_blocks_product_before_consent():
    call_command("seed_demo")
    workspace = Workspace.objects.get(slug="demo-workspace")
    product = Product.objects.get(workspace=workspace)
    provider = get_ai_provider()

    classification = provider.classify_message(
        message="Can anyone recommend a simple CRM for a small sales team?",
        product=product,
        consent_status=ConsentRecord.Status.NOT_REQUESTED,
    )
    draft = provider.generate_permission_request(message="Can anyone recommend a simple CRM for a small sales team?")

    assert classification.is_relevant is True
    assert classification.confidence >= 0.8
    assert "recommendation" in classification.intent_type
    assert "AI assistant" in draft.text
    assert validate_permission_first_response(draft.text).allowed is True

    blocked = validate_product_response(
        text=f"{product.name} starts at {product.starting_price} and you should buy it.",
        consent_status=ConsentRecord.Status.NOT_REQUESTED,
        product=product,
    )
    allowed = validate_product_response(
        text=f"{product.name} may help with follow-up tracking. Pricing starts at {product.starting_price} {product.currency}.",
        consent_status=ConsentRecord.Status.GRANTED,
        product=product,
    )

    assert blocked.allowed is False
    assert "consent_required" in blocked.flags
    assert allowed.allowed is True
