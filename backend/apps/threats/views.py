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
from apps.core.permissions import IsAdminOrReadOnly


class ThreatViewSet(viewsets.ModelViewSet):
    queryset = Threat.objects.all()
    serializer_class = ThreatSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity', 'status', 'threat_type']
    search_fields = ['source_ip', 'threat_type', 'notes']
    ordering_fields = ['detected_at', 'severity', 'confidence']
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        serializer = ThreatAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        prediction = ThreatDetectionService.predict(serializer.validated_data['features'])
        
        threat = Threat.objects.create(
            threat_type=prediction['threat_type'],
            severity=prediction['severity'],
            source_ip=serializer.validated_data['src_ip'],
            destination_ip=serializer.validated_data.get('dst_ip'),
            confidence=prediction['confidence'],
            raw_features=serializer.validated_data['features'],
            shap_explanation=prediction.get('shap_explanation'),
            lime_explanation=prediction.get('lime_explanation')
        )
        
        Alert.objects.create(
            title=f"{prediction['severity'].upper()}: {prediction['threat_type']} Detected",
            message=f"AI system detected {prediction['threat_type']} from {serializer.validated_data['src_ip']} with {(prediction['confidence'] * 100):.1f}% confidence.",
            severity=prediction['severity'],
            status='pending',
            threat=threat
        )
        
        Incident.objects.create(
            title=f"{prediction['threat_type']} - {serializer.validated_data['src_ip']}",
            description=f"Automated incident created from AI threat detection.\n\nThreat Type: {prediction['threat_type']}\nSource IP: {serializer.validated_data['src_ip']}\nDestination IP: {serializer.validated_data.get('dst_ip', 'N/A')}\nConfidence: {(prediction['confidence'] * 100):.1f}%\nSeverity: {prediction['severity']}\n\nThis incident is linked to the threat record for full traceability.",
            severity=prediction['severity'],
            status='open'
        )
        
        broadcast_threat(ThreatSerializer(threat).data)
        
        return Response(ThreatSerializer(threat).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        threat = self.get_object()
        threat.status = 'responded'
        threat.responded_at = timezone.now()
        
        action_taken = request.data.get('action_taken', '')
        notes = request.data.get('notes', '')
        severity_assessment = request.data.get('severity_assessment', threat.severity)
        
        response_info = f"\n\n--- RESPONSE RECORDED ---\nAction: {action_taken}\nSeverity Assessment: {severity_assessment}\nNotes: {notes}\nResponded by: {request.user.email}\nTimestamp: {timezone.now().isoformat()}"
        threat.notes = (threat.notes or '') + response_info
        threat.save()
        
        return Response({'status': 'threat responded', 'action_taken': action_taken})
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        threat = self.get_object()
        threat.status = 'resolved'
        threat.resolved_at = timezone.now()
        threat.notes = request.data.get('notes', '')
        threat.save()
        return Response({'status': 'threat resolved'})
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsAdminOrReadOnly])
    def dismiss(self, request, pk=None):
        threat = self.get_object()
        threat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="threats_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Threat Type', 'Severity', 'Source IP', 'Destination IP',
            'Confidence', 'Status', 'Detected At', 'Responded At', 'Resolved At', 'Notes'
        ])
        
        threats = self.filter_queryset(self.get_queryset())
        for threat in threats:
            writer.writerow([
                str(threat.id),
                threat.threat_type,
                threat.severity,
                threat.source_ip,
                threat.destination_ip or '',
                f"{threat.confidence * 100:.2f}%",
                threat.status,
                threat.detected_at.isoformat() if threat.detected_at else '',
                threat.responded_at.isoformat() if threat.responded_at else '',
                threat.resolved_at.isoformat() if threat.resolved_at else '',
                (threat.notes or '').replace('\n', ' ')
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Threat.objects.count()
        open_threats = Threat.objects.filter(status='open').count()
        critical = Threat.objects.filter(severity='critical').count()
        return Response({
            'total': total,
            'open': open_threats,
            'critical': critical
        })