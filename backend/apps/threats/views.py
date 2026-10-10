import csv
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse

from .models import Threat
from .serializers import ThreatSerializer, ThreatAnalyzeSerializer
from .services import ThreatDetectionService
from .consumers import broadcast_threat
from apps.alerts.models import Alert
from apps.incidents.models import Incident
from apps.settings.models import SystemSettings
from apps.core.permissions import IsAdmin

SEVERITIES = ('critical', 'high', 'medium', 'low')


def _csv_safe(value):
    s = '' if value is None else str(value)
    return "'" + s if s[:1] in ('=', '+', '-', '@', '\t', '\r') else s


class ThreatViewSet(viewsets.ModelViewSet):
    queryset = Threat.objects.all()
    serializer_class = ThreatSerializer
    filterset_fields = ['severity', 'status', 'threat_type']
    search_fields = ['source_ip', 'threat_type', 'notes']
    ordering_fields = ['detected_at', 'severity', 'confidence']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'dismiss'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        serializer = ThreatAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        prediction = ThreatDetectionService.predict(data['features'])
        cfg = SystemSettings.load()

        # GUARANTEE: Every field the frontend needs is present
        payload = {
            'is_threat': bool(prediction.get('is_threat', False)),
            'threat_type': str(prediction.get('threat_type', 'Unknown')),
            'severity': str(prediction.get('severity', 'low')),
            'confidence': float(prediction.get('confidence', 0.0)),
            'attack_probability': float(prediction.get('attack_probability', 0.0)),
            'rf_confidence': float(prediction.get('rf_confidence', 0.0)),
            'xgb_confidence': float(prediction.get('xgb_confidence', 0.0)),
            'threshold_used': float(prediction.get('threshold_used', cfg.confidence_threshold)),
            'source_ip': str(data.get('src_ip', '')),
            'destination_ip': str(data.get('dst_ip', '')),
            'features_provided': int(prediction.get('features_provided', 0)),
            'features_total': int(prediction.get('features_total', 0)),
            'unknown_features': list(prediction.get('unknown_features', [])),
            'shap_explanation': list(prediction.get('shap_explanation', [])),
            'lime_explanation': list(prediction.get('lime_explanation', [])),
            'response_time_ms': float(prediction.get('response_time_ms', 0.0)),
            'recorded': False,
        }

        if not payload['is_threat']:
            return Response(payload, status=status.HTTP_200_OK)

        threat = Threat.objects.create(
            threat_type=payload['threat_type'],
            severity=payload['severity'],
            source_ip=payload['source_ip'],
            destination_ip=payload['destination_ip'],
            confidence=payload['confidence'],
            raw_features=data['features'],
            shap_explanation=payload['shap_explanation'],
            lime_explanation=payload['lime_explanation'],
        )
        payload.update(recorded=True, id=str(threat.id), status=threat.status)

        if cfg.auto_create_alerts:
            Alert.objects.create(
                title=f"{payload['severity'].upper()}: {payload['threat_type']} Detected",
                message=(f"AI system detected {payload['threat_type']} from {payload['source_ip']} "
                         f"with {payload['confidence'] * 100:.1f}% confidence."),
                severity=payload['severity'], status='pending', threat=threat,
            )
        if cfg.auto_create_incidents:
            Incident.objects.create(
                title=f"{payload['threat_type']} - {payload['source_ip']}",
                description=(f"Automated incident from AI detection.\n\nThreat ID: {threat.id}\n"
                             f"Source IP: {payload['source_ip']}\n"
                             f"Destination IP: {payload['destination_ip'] or 'N/A'}\n"
                             f"Confidence: {payload['confidence'] * 100:.1f}%\n"
                             f"Severity: {payload['severity']}"),
                severity=payload['severity'], status='open',
                threat=threat,
            )
        if cfg.websocket_notifications:
            broadcast_threat(ThreatSerializer(threat).data)

        return Response(payload, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        threat = self.get_object()
        if threat.status != 'open':
            return Response({'error': f'Threat is already {threat.status}'},
                            status=status.HTTP_400_BAD_REQUEST)
        action_taken = (request.data.get('action_taken') or '').strip()
        notes = (request.data.get('notes') or '').strip()
        severity_assessment = request.data.get('severity_assessment') or threat.severity
        if not action_taken or not notes:
            return Response({'error': 'action_taken and notes are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        if severity_assessment not in SEVERITIES:
            return Response({'error': f"severity_assessment must be one of {', '.join(SEVERITIES)}"},
                            status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        threat.status = 'responded'
        threat.responded_at = now
        threat.notes = (threat.notes or '') + (
            f"\n\n--- RESPONSE RECORDED ---\nAction: {action_taken}\n"
            f"Severity Assessment: {severity_assessment}\nNotes: {notes}\n"
            f"Responded by: {request.user.email}\nTimestamp: {now.isoformat()}")
        threat.save()
        return Response({'status': 'threat responded', 'action_taken': action_taken})

    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        threat = self.get_object()
        if threat.status == 'resolved':
            return Response({'error': 'Threat is already resolved'},
                            status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        threat.status = 'resolved'
        threat.resolved_at = now
        extra = (request.data.get('notes') or '').strip()
        threat.notes = (threat.notes or '') + (
            f"\n\n--- RESOLVED ---\nResolved by: {request.user.email}\n"
            f"Timestamp: {now.isoformat()}" + (f"\nNotes: {extra}" if extra else ""))
        threat.save()
        return Response({'status': 'threat resolved'})

    @action(detail=True, methods=['delete'])
    def dismiss(self, request, pk=None):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="threats_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Threat Type', 'Severity', 'Source IP', 'Destination IP',
                         'Confidence', 'Status', 'Detected At', 'Responded At',
                         'Resolved At', 'Notes'])
        for t in self.filter_queryset(self.get_queryset()):
            writer.writerow([
                str(t.id), _csv_safe(t.threat_type), t.severity, t.source_ip,
                t.destination_ip or '', f"{t.confidence * 100:.2f}%", t.status,
                t.detected_at.isoformat() if t.detected_at else '',
                t.responded_at.isoformat() if t.responded_at else '',
                t.resolved_at.isoformat() if t.resolved_at else '',
                _csv_safe((t.notes or '').replace('\n', ' ')),
            ])
        return response

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response({
            'total': Threat.objects.count(),
            'open': Threat.objects.filter(status='open').count(),
            'critical': Threat.objects.filter(severity='critical').count(),
        })