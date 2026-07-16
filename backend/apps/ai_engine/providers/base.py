from dataclasses import dataclass
from typing import Protocol

from django.conf import settings

from apps.ai_engine.schemas import ClassificationResult, DraftResult
from apps.products.models import Product


class AIProvider(Protocol):
    def classify_message(self, *, message: str, product: Product, consent_status: str) -> ClassificationResult:
        ...

    def generate_permission_request(self, *, message: str) -> DraftResult:
        ...

    def generate_product_response(self, *, message: str, product: Product, consent_status: str) -> DraftResult:
        ...


@dataclass(frozen=True)
class AIProviderMetadata:
    provider: str
    model: str


def get_ai_provider_metadata(provider: AIProvider) -> AIProviderMetadata:
    provider_name = settings.AI_PROVIDER
    configured_models = {
        "mock": "mock",
        "gemini": settings.GEMINI_MODEL,
        "vertex": settings.VERTEX_MODEL,
    }
    return AIProviderMetadata(
        provider=provider_name,
        model=getattr(provider, "model", None) or configured_models.get(provider_name, ""),
    )
