from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import SystemSettings
from .serializers import SystemSettingsSerializer
from apps.core.permissions import IsAdminOrReadOnly, IsAdmin
from apps.threats.models import Threat
from apps.incidents.models import Incident
from apps.alerts.models import Alert

User = get_user_model()


class SystemSettingsView(APIView):
    """Get or update system settings. Read for all, write for admins only."""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get(self, request):
        settings = SystemSettings.load()
        serializer = SystemSettingsSerializer(settings)
        return Response(serializer.data)
    
    def patch(self, request):
        settings = SystemSettings.load()
        serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user.email)
        return Response(serializer.data)


class SystemHealthView(APIView):
    """System health and statistics (admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Database size (SQLite)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
                db_size_bytes = cursor.fetchone()[0]
                db_size_mb = round(db_size_bytes / (1024 * 1024), 2)
        except Exception:
            db_size_mb = 0
        
        # Counts
        total_threats = Threat.objects.count()
        total_incidents = Incident.objects.count()
        total_alerts = Alert.objects.count()
        total_users = User.objects.count()
        
        # Recent activity (last 24h)
        last_24h = timezone.now() - timezone.timedelta(hours=24)
        threats_24h = Threat.objects.filter(detected_at__gte=last_24h).count()
        incidents_24h = Incident.objects.filter(created_at__gte=last_24h).count()
        
        # Critical counts
        critical_threats = Threat.objects.filter(severity='critical').count()
        open_incidents = Incident.objects.filter(status='open').count()
        pending_alerts = Alert.objects.filter(status='pending').count()
        
        return Response({
            'database': {
                'size_mb': db_size_mb,
                'engine': 'SQLite',
            },
            'totals': {
                'threats': total_threats,
                'incidents': total_incidents,
                'alerts': total_alerts,
                'users': total_users,
            },
            'last_24h': {
                'threats': threats_24h,
                'incidents': incidents_24h,
            },
            'critical': {
                'threats': critical_threats,
                'open_incidents': open_incidents,
                'pending_alerts': pending_alerts,
            },
            'server_time': timezone.now().isoformat(),
        })