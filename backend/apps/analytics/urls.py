from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardAnalyticsView.as_view(), name='analytics-dashboard'),
]