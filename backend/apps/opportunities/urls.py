from django.urls import path

from apps.opportunities.views import ApprovalQueueView, ApproveDraftView, OpportunityDetailView, OpportunityListView


urlpatterns = [
    path("opportunities/", OpportunityListView.as_view(), name="opportunity-list"),
    path("opportunities/<uuid:pk>/", OpportunityDetailView.as_view(), name="opportunity-detail"),
    path("approvals/", ApprovalQueueView.as_view(), name="approval-queue"),
    path("approvals/<uuid:pk>/approve/", ApproveDraftView.as_view(), name="approve-draft"),
]
