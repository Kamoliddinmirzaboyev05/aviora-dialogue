from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request):
    return Response({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/ai/", include("apps.ai_engine.urls")),
    path("api/v1/workspaces/", include("apps.workspaces.urls")),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/v1/triggers/", include("apps.triggers.urls")),
    path("api/v1/telegram/", include("apps.telegram_integration.urls")),
    path("api/v1/", include("apps.opportunities.urls")),
    path("api/v1/conversations/", include("apps.conversations.urls")),
    path("api/v1/leads/", include("apps.leads.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/audit-logs/", include("apps.audit_logs.urls")),
]
