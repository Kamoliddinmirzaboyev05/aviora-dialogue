from typing import TypeVar

from django.conf import settings
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from apps.ai_engine.exceptions import AIProviderConfigurationError, AIProviderError
from apps.ai_engine.schemas import ClassificationResult, DraftResult
from apps.products.models import Product


class GeminiClassification(BaseModel):
    is_relevant: bool
    intent_type: str
    confidence: float = Field(ge=0, le=1)
    detected_problem: str
    urgency: str
    language: str
    sentiment: str
    recommended_action: str
    concise_reason: str
    risk_flags: list[str]


class GeminiDraft(BaseModel):
    text: str
    concise_reason: str
    safety_flags: list[str] = Field(default_factory=list)


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


class GeminiAPIProvider:
    def __init__(self, *, api_key: str | None = None, model: str | None = None, client=None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model if model is not None else settings.GEMINI_MODEL
        if not self.api_key:
            raise AIProviderConfigurationError("Gemini API provider requires GEMINI_API_KEY.")
        self.client = client if client is not None else genai.Client(api_key=self.api_key)

    def classify_message(self, *, message: str, product: Product, consent_status: str) -> ClassificationResult:
        normalized = self._generate(
            prompt=(
                "Classify the incoming message for ethical product outreach. Return whether it is relevant, "
                "its intent, confidence, detected problem, urgency, language, sentiment, recommended action, "
                "concise reason, and risk flags.\n"
                f"Message: {message}\n"
                f"Product: {self._product_context(product)}\n"
                f"Consent status: {consent_status}"
            ),
            response_model=GeminiClassification,
        )
        return ClassificationResult(**normalized.model_dump())

    def generate_permission_request(self, *, message: str) -> DraftResult:
        normalized = self._generate(
            prompt=(
                "Write a transparent, permission-first reply to this message. Identify the assistant as AI, "
                "do not promote a product, and ask whether the recipient wants more information.\n"
                f"Message: {message}"
            ),
            response_model=GeminiDraft,
        )
        return DraftResult(**normalized.model_dump())

    def generate_product_response(self, *, message: str, product: Product, consent_status: str) -> DraftResult:
        normalized = self._generate(
            prompt=(
                "Write a factual product response only for a recipient who has already granted consent. "
                "Use only the supplied product context, disclose that the assistant is AI, and do not invent details.\n"
                f"Message: {message}\n"
                f"Product: {self._product_context(product)}\n"
                f"Consent status: {consent_status}"
            ),
            response_model=GeminiDraft,
        )
        return DraftResult(**normalized.model_dump())

    def _generate(self, *, prompt: str, response_model: type[ResponseModel]) -> ResponseModel:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )
            return response_model.model_validate(response.parsed)
        except Exception as error:
            raise AIProviderError(
                "Gemini request failed. Check provider configuration and service availability."
            ) from error

    @staticmethod
    def _product_context(product: Product) -> str:
        return (
            f"name={product.name}; target_customer={product.target_customer}; "
            f"problems_solved={product.problems_solved}; benefits={product.benefits}; "
            f"pricing_model={product.pricing_model}; starting_price={product.starting_price}; "
            f"currency={product.currency}; website={product.website}"
        )
