from django.urls import path
from .views import (
    AdminDashboardStatsView,
    AdminAnalyticsChartsView,
    AdminRecentOrdersView,
)

urlpatterns = [
    path('dashboard/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('analytics/', AdminAnalyticsChartsView.as_view(), name='admin-analytics-charts'),
    path('recent-orders/', AdminRecentOrdersView.as_view(), name='admin-recent-orders'),
]
