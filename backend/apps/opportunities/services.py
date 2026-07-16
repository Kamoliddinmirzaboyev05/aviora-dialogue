from django.db import transaction
from django.utils import timezone
import re

from apps.ai_engine.safety import validate_permission_first_response, validate_product_response
from apps.ai_engine.services import get_ai_provider
from apps.audit_logs.services import record_audit
from apps.consent.models import ConsentRecord
from apps.conversations.models import Conversation, Message
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity, ResponseDraft
from apps.products.models import Product
from apps.telegram_integration.models import TelegramChat, TelegramConnection, TelegramContact
from apps.telegram_integration.services import get_telegram_provider
from apps.triggers.models import TriggerSet
from apps.triggers.services import match_trigger_set


@transaction.atomic
def simulate_incoming_message(
    *,
    workspace,
    actor,
    message: str,
    sender_name: str,
    telegram_user_id: str,
    connection=None,
    chat=None,
):
    connection = connection or TelegramConnection.objects.filter(
        workspace=workspace, provider="mock", is_active=True
    ).first()
    chat = chat or TelegramChat.objects.filter(
        workspace=workspace, monitoring_enabled=True
    ).first()
    product = Product.objects.filter(workspace=workspace, status="active").first()
    trigger = TriggerSet.objects.filter(workspace=workspace, enabled=True).first()
    if not (connection and chat and product and trigger):
        raise ValueError("Demo workspace is missing connection, chat, product, or trigger.")

    contact, _ = TelegramContact.objects.get_or_create(
        workspace=workspace,
        telegram_user_id=telegram_user_id,
        defaults={"display_name": sender_name},
    )
    trigger_match = match_trigger_set(message, trigger)
    provider = get_ai_provider()
    classification = provider.classify_message(
        message=message,
        product=product,
        consent_status=ConsentRecord.Status.NOT_REQUESTED,
    )

    if not trigger_match.is_match or not classification.is_relevant:
        return {"opportunity": None, "draft": None}

    opportunity = Opportunity.objects.create(
        workspace=workspace,
        chat=chat,
        contact=contact,
        product=product,
        trigger_set=trigger,
        source_message=message,
        detected_intent=classification.intent_type,
        relevance_score=trigger_match.score,
        confidence=classification.confidence,
        concise_reason=classification.concise_reason,
    )
    draft_result = provider.generate_permission_request(message=message)
    safety = validate_permission_first_response(draft_result.text)
    draft = ResponseDraft.objects.create(
        workspace=workspace,
        opportunity=opportunity,
        text=draft_result.text,
        safety_flags=safety.flags,
    )
    record_audit(
        workspace=workspace,
        actor=actor,
        action="opportunity.created",
        resource=opportunity,
        summary=classification.concise_reason,
        metadata={"trigger_score": trigger_match.score, "confidence": classification.confidence},
    )
    return {"opportunity": opportunity, "draft": draft}


@transaction.atomic
def approve_permission_draft(*, draft: ResponseDraft, actor):
    opportunity = draft.opportunity
    provider = get_telegram_provider()
    sent = provider.send_message(chat_id=opportunity.chat.telegram_chat_id, text=draft.text)

    conversation, _ = Conversation.objects.get_or_create(
        workspace=draft.workspace,
        opportunity=opportunity,
        defaults={
            "chat": opportunity.chat,
            "contact": opportunity.contact,
            "product": opportunity.product,
            "consent_status": ConsentRecord.Status.REQUEST_SENT,
            "summary": opportunity.concise_reason,
        },
    )
    Message.objects.get_or_create(
        workspace=draft.workspace,
        conversation=conversation,
        direction="inbound",
        body=opportunity.source_message,
        defaults={"source": "telegram", "delivery_state": "received"},
    )
    Message.objects.create(
        workspace=draft.workspace,
        conversation=conversation,
        direction="outbound",
        body=draft.text,
        source="ai",
        delivery_state=sent.delivery_state,
        metadata={"provider_message_id": sent.provider_message_id},
    )
    ConsentRecord.objects.create(
        workspace=draft.workspace,
        contact=opportunity.contact,
        conversation=conversation,
        status=ConsentRecord.Status.REQUEST_SENT,
        request_message=draft.text,
        evidence_reference=sent.provider_message_id,
    )
    draft.status = ResponseDraft.Status.SENT
    draft.approved_by = actor
    draft.sent_at = timezone.now()
    draft.save(update_fields=["status", "approved_by", "sent_at", "updated_at"])
    opportunity.status = Opportunity.Status.PERMISSION_REQUESTED
    opportunity.save(update_fields=["status", "updated_at"])
    record_audit(workspace=draft.workspace, actor=actor, action="draft.approved", resource=draft, summary="Permission request sent.")
    return conversation


@transaction.atomic
def simulate_consent_reply(*, conversation: Conversation, message: str):
    Message.objects.create(
        workspace=conversation.workspace,
        conversation=conversation,
        direction="inbound",
        body=message,
        source="telegram",
        delivery_state="received",
    )
    normalized = message.lower()
    denied = bool(re.search(r"\b(no|nah|nope|stop|do not|don't|dont|not now|yo'q)\b", normalized))
    granted = not denied and bool(re.search(r"\b(yes|please|send|ok|okay|ha|sure)\b", normalized))
    status = ConsentRecord.Status.GRANTED if granted else ConsentRecord.Status.DENIED
    consent = ConsentRecord.objects.filter(conversation=conversation).order_by("-created_at").first()
    if not consent:
        consent = ConsentRecord.objects.create(workspace=conversation.workspace, contact=conversation.contact, conversation=conversation)
    consent.status = status
    consent.response_message = message
    consent.granted_at = timezone.now() if granted else None
    consent.save(update_fields=["status", "response_message", "granted_at", "updated_at"])
    conversation.consent_status = status
    conversation.save(update_fields=["consent_status", "updated_at"])
    if conversation.opportunity:
        conversation.opportunity.status = Opportunity.Status.CONSENT_RECEIVED if granted else Opportunity.Status.REJECTED
        conversation.opportunity.save(update_fields=["status", "updated_at"])
    return consent


@transaction.atomic
def generate_product_response(*, conversation: Conversation):
    if conversation.consent_status != ConsentRecord.Status.GRANTED:
        raise PermissionError("Consent is required before product information can be sent.")
    provider = get_ai_provider()
    latest_message = conversation.messages.order_by("-created_at").first()
    draft = provider.generate_product_response(
        message=latest_message.body if latest_message else "",
        product=conversation.product,
        consent_status=conversation.consent_status,
    )
    safety = validate_product_response(text=draft.text, consent_status=conversation.consent_status, product=conversation.product)
    if not safety.allowed:
        raise PermissionError(",".join(safety.flags))
    return Message.objects.create(
        workspace=conversation.workspace,
        conversation=conversation,
        direction="outbound",
        body=draft.text,
        source="ai",
        delivery_state="sent",
        metadata={"safety_flags": safety.flags},
    )


@transaction.atomic
def convert_conversation_to_lead(*, workspace, conversation: Conversation, actor=None):
    if conversation.consent_status != ConsentRecord.Status.GRANTED:
        raise PermissionError("Consent is required before converting a conversation to a lead.")
    lead, _ = Lead.objects.get_or_create(
        workspace=workspace,
        conversation=conversation,
        defaults={
            "contact": conversation.contact,
            "product": conversation.product,
            "detected_need": conversation.summary or "Interested in product information after consent.",
            "score": conversation.opportunity.relevance_score if conversation.opportunity else 70,
            "assigned_manager": actor,
        },
    )
    if conversation.opportunity:
        conversation.opportunity.status = Opportunity.Status.CONVERTED_TO_LEAD
        conversation.opportunity.save(update_fields=["status", "updated_at"])
    return lead
