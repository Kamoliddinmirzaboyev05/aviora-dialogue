from django.conf import settings

from apps.ai_engine.providers.mock import MockAIProvider
from apps.ai_engine.providers.vertex import VertexAIProvider


def get_ai_provider():
    if settings.AI_PROVIDER == "vertex":
        return VertexAIProvider()
    return MockAIProvider()
