from django.conf import settings

from apps.ai_engine.providers.mock import MockAIProvider


class VertexAIProvider(MockAIProvider):
    """Vertex provider shell.

    The local MVP keeps mock behavior unless real credentials are supplied. The
    class validates platform-managed configuration so production wiring can fail
    loudly instead of silently falling back.
    """

    def __init__(self):
        missing = [
            name
            for name, value in {
                "VERTEX_PROJECT_ID": settings.VERTEX_PROJECT_ID,
                "VERTEX_LOCATION": settings.VERTEX_LOCATION,
                "VERTEX_MODEL": settings.VERTEX_MODEL,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Vertex AI is not configured: {', '.join(missing)}")
