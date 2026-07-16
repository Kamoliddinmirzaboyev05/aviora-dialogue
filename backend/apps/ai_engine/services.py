from django.conf import settings

from apps.ai_engine.exceptions import AIProviderConfigurationError
from apps.ai_engine.providers.gemini import GeminiAPIProvider
from apps.ai_engine.providers.mock import MockAIProvider
from apps.ai_engine.providers.vertex import VertexAIProvider


def get_ai_provider():
    providers = {
        "mock": MockAIProvider,
        "gemini": GeminiAPIProvider,
        "vertex": VertexAIProvider,
    }
    try:
        return providers[settings.AI_PROVIDER]()
    except KeyError as error:
        raise AIProviderConfigurationError(f"Unsupported AI_PROVIDER: {settings.AI_PROVIDER}") from error
