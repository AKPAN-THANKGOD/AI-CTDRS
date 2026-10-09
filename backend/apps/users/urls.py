from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Set up the router for the ViewSet
router = DefaultRouter()
router.register(r'management', views.UserManagementViewSet, basename='user-management')

urlpatterns = [
    # Standard auth endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Router URLs (handles /management/ and /management/<id>/)
    path('', include(router.urls)),
]