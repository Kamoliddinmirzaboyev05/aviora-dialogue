from django.urls import path

from apps.analytics.views import OverviewAnalyticsView


urlpatterns = [
    path("overview/", OverviewAnalyticsView.as_view(), name="analytics-overview"),
]
