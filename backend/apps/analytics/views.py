# LOCATION: backend/apps/analytics/views.py
from datetime import datetime, time, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.threats.models import Threat
from apps.incidents.models import Incident
from apps.alerts.models import Alert

WINDOW_DAYS = 30


def _fmt_duration(td):
    if td is None:
        return "N/A"
    secs = int(td.total_seconds())
    if secs < 60:
        return f"{secs} secs"
    if secs < 3600:
        return f"{secs / 60:.1f} mins"
    if secs < 86400:
        return f"{secs / 3600:.1f} hrs"
    return f"{secs / 86400:.1f} days"


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        first_day = today - timedelta(days=WINDOW_DAYS - 1)      # window INCLUDES today
        start = timezone.make_aware(datetime.combine(first_day, time.min))

        in_window = Threat.objects.filter(detected_at__gte=start)

        # 1. Trend: every day of the window, zero-filled
        counts = {r['date']: r['count'] for r in
                  in_window.annotate(date=TruncDate('detected_at')).values('date').annotate(count=Count('id'))}
        trends = [{'date': (first_day + timedelta(days=i)).isoformat(),
                   'count': counts.get(first_day + timedelta(days=i), 0)}
                  for i in range(WINDOW_DAYS)]

        # 2. Top source IPs
        top_ips = list(in_window.values('source_ip').annotate(count=Count('id')).order_by('-count')[:10])

        # 3. Severity distribution
        sev = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for r in in_window.values('severity').annotate(count=Count('id')):
            if r['severity'] in sev:
                sev[r['severity']] = r['count']

        # 4. Analyst performance (resolved incidents per assignee)
        perf = (Incident.objects.filter(status='resolved', resolved_at__gte=start)
                .values('assigned_to__full_name', 'assigned_to__email')
                .annotate(resolved_count=Count('id')).order_by('-resolved_count')[:5])

        # 5. Real mean time to respond: detected_at -> responded_at
        avg_td = (Threat.objects.filter(responded_at__isnull=False)
                  .annotate(delta=ExpressionWrapper(F('responded_at') - F('detected_at'),
                                                    output_field=DurationField()))
                  .aggregate(avg=Avg('delta'))['avg'])

        return Response({
            'summary': {
                'total_threats': Threat.objects.count(),
                'critical_threats': Threat.objects.filter(severity='critical').count(),
                'open_incidents': Incident.objects.filter(status__in=['open', 'in_progress']).count(),
                'pending_alerts': Alert.objects.filter(status='pending').count(),
                'avg_response_time': _fmt_duration(avg_td),
            },
            'threat_trends': trends,
            'top_ips': top_ips,
            'severity_distribution': sev,
            'analyst_performance': [{
                'name': r['assigned_to__full_name'] or r['assigned_to__email'] or 'Unassigned',
                'resolved': r['resolved_count'],
            } for r in perf],
        })