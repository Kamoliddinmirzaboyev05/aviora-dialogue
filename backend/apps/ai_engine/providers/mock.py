from apps.ai_engine.schemas import ClassificationResult, DraftResult
from apps.products.models import Product


class MockAIProvider:
    def classify_message(self, *, message: str, product: Product, consent_status: str) -> ClassificationResult:
        text = message.lower()
        is_crm_request = "crm" in text and ("recommend" in text or "simple" in text or "sales team" in text)
        return ClassificationResult(
            is_relevant=is_crm_request,
            intent_type="recommendation_request" if is_crm_request else "irrelevant",
            confidence=0.92 if is_crm_request else 0.18,
            detected_problem="Needs a simple CRM for a small sales team" if is_crm_request else "",
            urgency="medium" if is_crm_request else "low",
            language="en",
            sentiment="neutral",
            recommended_action="draft_permission_request" if is_crm_request else "ignore",
            concise_reason="The sender asks for a simple CRM recommendation for a small sales team."
            if is_crm_request
            else "The message does not match the configured product intent.",
            risk_flags=[],
        )

    def generate_permission_request(self, *, message: str) -> DraftResult:
        return DraftResult(
            text=(
                "Hi, I am an AI assistant for a business that helps small teams with CRM workflows. "
                "I noticed your question and can share a relevant suggestion if you want. "
                "Would you like me to send more information?"
            ),
            concise_reason="Transparent permission-first reply with AI disclosure and no promotion before consent.",
        )

    def generate_product_response(self, *, message: str, product: Product, consent_status: str) -> DraftResult:
        return DraftResult(
            text=(
                f"Thanks for confirming. {product.name} may fit because it helps {product.target_customer.lower()} "
                f"with {product.problems_solved.lower()} Key benefits include {product.benefits.lower()} "
                f"Pricing starts at {product.starting_price} {product.currency} on a {product.pricing_model} basis. "
                f"You can review details here: {product.website}"
            ),
            concise_reason="Grounded response generated from enabled product fields after consent.",
        )
