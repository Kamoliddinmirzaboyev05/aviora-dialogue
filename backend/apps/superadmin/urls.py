from django.urls import path

from apps.superadmin.views import (
    IntegrationStatusView,
    PlatformOverviewView,
    RecentEventsView,
    UserListView,
    WorkspaceListView,
)


urlpatterns = [
    path("overview/", PlatformOverviewView.as_view(), name="superadmin-overview"),
    path("workspaces/", WorkspaceListView.as_view(), name="superadmin-workspace-list"),
    path("users/", UserListView.as_view(), name="superadmin-user-list"),
    path("integrations/", IntegrationStatusView.as_view(), name="superadmin-integrations"),
    path("events/", RecentEventsView.as_view(), name="superadmin-events"),
]
