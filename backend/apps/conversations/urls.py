from django.urls import path

from apps.conversations.views import (
    ConversationDetailView,
    ConversationListView,
    GenerateProductResponseView,
    SimulateConsentView,
)


urlpatterns = [
    path("", ConversationListView.as_view(), name="conversation-list"),
    path("<uuid:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path("<uuid:pk>/simulate-consent/", SimulateConsentView.as_view(), name="simulate-consent"),
    path("<uuid:pk>/generate-product-response/", GenerateProductResponseView.as_view(), name="generate-product-response"),
]
