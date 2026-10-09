# LOCATION: backend/apps/settings/views.py
from datetime import timedelta

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
    """Read: any authenticated user. Write: admins only."""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request):
        return Response(SystemSettingsSerializer(SystemSettings.load()).data)

    def patch(self, request):
        serializer = SystemSettingsSerializer(SystemSettings.load(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user.email)
        return Response(serializer.data)


def _db_info():
    """Database size and engine name for SQLite or PostgreSQL."""
    vendor = connection.vendor
    size_bytes = 0
    try:
        with connection.cursor() as cur:
            if vendor == 'sqlite':
                cur.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
            elif vendor == 'postgresql':
                cur.execute("SELECT pg_database_size(current_database())")
            else:
                cur.execute("SELECT 0")
            size_bytes = cur.fetchone()[0] or 0
    except Exception:
        size_bytes = 0
    names = {'sqlite': 'SQLite', 'postgresql': 'PostgreSQL'}
    return {'size_mb': round(size_bytes / (1024 * 1024), 2),
            'engine': names.get(vendor, vendor)}


class SystemHealthView(APIView):
    """System health and statistics (admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        since = timezone.now() - timedelta(hours=24)
        return Response({
            'database': _db_info(),
            'totals': {'threats': Threat.objects.count(), 'incidents': Incident.objects.count(),
                       'alerts': Alert.objects.count(), 'users': User.objects.count()},
            'last_24h': {'threats': Threat.objects.filter(detected_at__gte=since).count(),
                         'incidents': Incident.objects.filter(created_at__gte=since).count()},
            'critical': {
                'threats': Threat.objects.filter(severity='critical').count(),
                'open_incidents': Incident.objects.filter(status__in=['open', 'in_progress']).count(),
                'pending_alerts': Alert.objects.filter(status='pending').count()},
            'server_time': timezone.now().isoformat(),
        })