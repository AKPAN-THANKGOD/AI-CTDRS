from django.urls import path
from . import views

urlpatterns = [
    path('', views.SystemSettingsView.as_view(), name='system-settings'),
    path('health/', views.SystemHealthView.as_view(), name='system-health'),
]