from django.urls import path

from apps.ai_engine.views import AIConnectionTestView


urlpatterns = [
    path("test-connection/", AIConnectionTestView.as_view(), name="ai-test-connection"),
]
