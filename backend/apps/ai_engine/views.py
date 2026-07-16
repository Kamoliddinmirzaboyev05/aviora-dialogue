from dataclasses import asdict
from time import perf_counter

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_engine.exceptions import AIProviderConfigurationError, AIProviderError
from apps.ai_engine.permissions import get_workspace_admin_membership
from apps.ai_engine.providers.base import get_ai_provider_metadata
from apps.ai_engine.services import get_ai_provider
from apps.common.api import api_error
from apps.products.models import Product


CONNECTION_TEST_MESSAGE = "Can you recommend a simple CRM for a small sales team?"


class AIConnectionTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership = get_workspace_admin_membership(request)
        if not membership:
            return api_error("workspace_admin_required", "Workspace owner or admin access is required.", status=403)

        product = Product.objects.filter(workspace=membership.workspace, status="active").order_by("created_at").first()
        if not product:
            return api_error("active_product_required", "An active workspace product is required.", status=400)

        started_at = perf_counter()
        try:
            provider = get_ai_provider()
            classification = provider.classify_message(
                message=CONNECTION_TEST_MESSAGE,
                product=product,
                consent_status="not_requested",
            )
        except (AIProviderConfigurationError, AIProviderError) as error:
            return api_error("ai_connection_failed", str(error), status=503)

        metadata = get_ai_provider_metadata(provider)
        return Response(
            {
                "provider": metadata.provider,
                "model": metadata.model,
                "state": "connected",
                "latency_ms": int((perf_counter() - started_at) * 1000),
                "classification": asdict(classification),
            }
        )
