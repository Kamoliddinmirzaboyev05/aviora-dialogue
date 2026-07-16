from django.urls import path

from apps.leads.views import ConvertLeadView, LeadListView, LeadUpdateView


urlpatterns = [
    path("", LeadListView.as_view(), name="lead-list"),
    path("convert/", ConvertLeadView.as_view(), name="lead-convert"),
    path("<uuid:pk>/", LeadUpdateView.as_view(), name="lead-update"),
]
