from typing import Protocol

from apps.ai_engine.schemas import ClassificationResult, DraftResult
from apps.products.models import Product


class AIProvider(Protocol):
    def classify_message(self, *, message: str, product: Product, consent_status: str) -> ClassificationResult:
        ...

    def generate_permission_request(self, *, message: str) -> DraftResult:
        ...

    def generate_product_response(self, *, message: str, product: Product, consent_status: str) -> DraftResult:
        ...
