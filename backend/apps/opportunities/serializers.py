from rest_framework import serializers

from apps.conversations.models import Conversation, Message
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity, ResponseDraft


class OpportunitySerializer(serializers.ModelSerializer):
    chat_title = serializers.CharField(source="chat.title", read_only=True)
    contact_name = serializers.CharField(source="contact.display_name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "workspace",
            "chat_title",
            "contact_name",
            "product_name",
            "source_message",
            "detected_intent",
            "relevance_score",
            "confidence",
            "concise_reason",
            "status",
            "created_at",
        ]


class ResponseDraftSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)

    class Meta:
        model = ResponseDraft
        fields = ["id", "workspace", "opportunity", "draft_type", "text", "status", "safety_flags", "sent_at", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "direction", "body", "source", "delivery_state", "metadata", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.display_name", read_only=True)
    chat_title = serializers.CharField(source="chat.title", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "workspace",
            "contact_name",
            "chat_title",
            "product_name",
            "consent_status",
            "status",
            "summary",
            "messages",
            "created_at",
        ]


class LeadSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.display_name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Lead
        fields = ["id", "workspace", "contact_name", "product_name", "detected_need", "score", "status", "created_at"]
        read_only_fields = ["workspace", "contact_name", "product_name", "detected_need", "score", "created_at"]
