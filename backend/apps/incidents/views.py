from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO

from .models import Incident, IncidentNote
from .serializers import IncidentSerializer, IncidentNoteSerializer
from apps.core.permissions import IsAdminOrReadOnly


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('-created_at')
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity', 'status', 'assigned_to']
    search_fields = ['title', 'description']
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        incident = self.get_object()
        incident.assigned_to = request.user
        incident.status = 'in_progress'
        incident.save()
        return Response({'status': 'incident assigned'})
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        incident = self.get_object()
        serializer = IncidentNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(incident=incident, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        incident = self.get_object()
        incident.status = 'resolved'
        incident.resolved_at = timezone.now()
        incident.save()
        
        if request.data.get('note'):
            IncidentNote.objects.create(
                incident=incident,
                author=request.user,
                content=request.data['note']
            )
        
        return Response({'status': 'incident resolved'})
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsAdminOrReadOnly])
    def dismiss(self, request, pk=None):
        incident = self.get_object()
        incident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=20,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=10,
            spaceBefore=15,
        )
        
        elements = []
        
        elements.append(Paragraph("AI-CTDRS Incident Report", title_style))
        elements.append(Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        incidents = self.filter_queryset(self.get_queryset())
        total = incidents.count()
        open_count = incidents.filter(status='open').count()
        critical_count = incidents.filter(severity='critical').count()
        
        elements.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ['Total Incidents', str(total)],
            ['Open Incidents', str(open_count)],
            ['Critical Incidents', str(critical_count)],
        ]
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Incident Details", heading_style))
        
        table_data = [['Title', 'Severity', 'Status', 'Assigned To', 'Created']]
        for incident in incidents[:50]:
            assigned = incident.assigned_to.email if incident.assigned_to else 'Unassigned'
            table_data.append([
                Paragraph(incident.title[:40], styles['Normal']),
                incident.severity.capitalize(),
                incident.status.replace('_', ' ').title(),
                assigned,
                incident.created_at.strftime('%Y-%m-%d')
            ])
        
        incident_table = Table(table_data, colWidths=[2.2*inch, 0.9*inch, 1*inch, 1.5*inch, 1*inch])
        incident_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(incident_table)
        
        doc.build(elements)
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="incident_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response