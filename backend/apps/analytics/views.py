from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from apps.threats.models import Threat
from apps.incidents.models import Incident
from apps.alerts.models import Alert
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # 1. Threat Trends (Last 30 Days)
        threat_trends = (
            Threat.objects.filter(detected_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('detected_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Format for frontend chart (ensure all 30 days have a value, even 0)
        dates = [(thirty_days_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        trend_data = {date: 0 for date in dates}
        for item in threat_trends:
            date_str = item['date'].strftime('%Y-%m-%d')
            if date_str in trend_data:
                trend_data[date_str] = item['count']
        
        threat_trends_formatted = [
            {'date': date, 'count': count} for date, count in trend_data.items()
        ]

        # 2. Top Attacking IPs
        top_ips = (
            Threat.objects.filter(detected_at__gte=thirty_days_ago)
            .values('source_ip')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # 3. Severity Distribution
        severity_dist = (
            Threat.objects.filter(detected_at__gte=thirty_days_ago)
            .values('severity')
            .annotate(count=Count('id'))
        )
        severity_map = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for item in severity_dist:
            if item['severity'] in severity_map:
                severity_map[item['severity']] = item['count']

        # 4. Analyst Performance (Incidents resolved per user)
        incident_performance = (
            Incident.objects.filter(resolved_at__gte=thirty_days_ago, status='resolved')
            .values('assigned_to__full_name', 'assigned_to__email')
            .annotate(resolved_count=Count('id'))
            .order_by('-resolved_count')[:5]
        )

        # 5. Summary Metrics
        total_threats = Threat.objects.count()
        critical_threats = Threat.objects.filter(severity='critical').count()
        open_incidents = Incident.objects.filter(status='open').count()
        pending_alerts = Alert.objects.filter(status='pending').count()
        
        # Average response time (mocked calculation for demo, or real if you track it)
        avg_response_time = "12.5 mins" 

        return Response({
            'summary': {
                'total_threats': total_threats,
                'critical_threats': critical_threats,
                'open_incidents': open_incidents,
                'pending_alerts': pending_alerts,
                'avg_response_time': avg_response_time,
            },
            'threat_trends': threat_trends_formatted,
            'top_ips': list(top_ips),
            'severity_distribution': severity_map,
            'analyst_performance': [
                {
                    'name': item['assigned_to__full_name'] or item['assigned_to__email'] or 'Unassigned',
                    'resolved': item['resolved_count']
                }
                for item in incident_performance
            ]
        })