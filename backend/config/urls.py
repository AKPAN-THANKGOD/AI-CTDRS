from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/threats/', include('apps.threats.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/settings/', include('apps.settings.urls')),   # 👈 ADD THIS LINE
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]