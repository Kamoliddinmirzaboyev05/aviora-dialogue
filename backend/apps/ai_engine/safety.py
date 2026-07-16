from apps.ai_engine.schemas import SafetyResult
from apps.consent.models import ConsentRecord
from apps.products.models import Product


PROMOTIONAL_WORDS = ("buy", "pricing", "starts at", "book", "demo", "benefits", "features")


def validate_permission_first_response(text: str) -> SafetyResult:
    flags = []
    lowered = text.lower()
    if "ai assistant" not in lowered and "automated" not in lowered:
        flags.append("missing_ai_disclosure")
    if "would you like" not in lowered and "if you want" not in lowered:
        flags.append("missing_permission_request")
    return SafetyResult(not flags, flags, "Permission request is transparent." if not flags else "Permission draft failed safety checks.")


def validate_product_response(*, text: str, consent_status: str, product: Product) -> SafetyResult:
    flags = []
    lowered = text.lower()
    has_promotion = product.name.lower() in lowered or any(word in lowered for word in PROMOTIONAL_WORDS)
    if consent_status != ConsentRecord.Status.GRANTED and has_promotion:
        flags.append("consent_required")
    if product.starting_price and str(product.starting_price) not in text and "pricing" in lowered:
        flags.append("unsupported_price")
    return SafetyResult(not flags, flags, "Product response passed safety checks." if not flags else "Product response blocked.")
