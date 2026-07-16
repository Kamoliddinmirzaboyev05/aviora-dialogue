from django.urls import path

from apps.triggers.views import TriggerSetDetailView, TriggerSetListCreateView


urlpatterns = [
    path("", TriggerSetListCreateView.as_view(), name="trigger-list"),
    path("<uuid:pk>/", TriggerSetDetailView.as_view(), name="trigger-detail"),
]
