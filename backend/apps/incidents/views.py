# LOCATION: backend/apps/incidents/views.py
from io import BytesIO
from xml.sax.saxutils import escape

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

from .models import Incident, IncidentNote
from .serializers import IncidentSerializer, IncidentNoteSerializer
from apps.core.permissions import IsAdmin


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.select_related('assigned_to', 'threat').prefetch_related('notes')
    serializer_class = IncidentSerializer
    filterset_fields = ['severity', 'status', 'assigned_to']
    search_fields = ['title', 'description']

    def get_permissions(self):
        # Analysts may create incidents and work them (assign / note / resolve).
        # Editing fields directly and deleting are admin only.
        if self.action in ('update', 'partial_update', 'destroy', 'dismiss'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(status='open')

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
        if incident.status in ('resolved', 'closed'):
            return Response({'error': 'Incident is already resolved'},
                            status=status.HTTP_400_BAD_REQUEST)
        incident.status = 'resolved'
        incident.resolved_at = timezone.now()
        if incident.assigned_to is None:       # credit the analyst who resolved it
            incident.assigned_to = request.user
        incident.save()
        if request.data.get('note'):
            IncidentNote.objects.create(incident=incident, author=request.user,
                                        content=request.data['note'])
        return Response({'status': 'incident resolved'})

    @action(detail=True, methods=['delete'])
    def dismiss(self, request, pk=None):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18,
                                     textColor=colors.HexColor('#1e40af'), spaceAfter=20)
        heading = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14,
                                 textColor=colors.HexColor('#1e3a8a'), spaceAfter=10, spaceBefore=15)
        incidents = self.filter_queryset(self.get_queryset())
        total = incidents.count()

        els = [Paragraph("AI-CTDRS Incident Report", title_style),
               Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']),
               Spacer(1, 20), Paragraph("Executive Summary", heading)]
        summary = Table([
            ['Total Incidents', str(total)],
            ['Open Incidents', str(incidents.filter(status__in=['open', 'in_progress']).count())],
            ['Critical Incidents', str(incidents.filter(severity='critical').count())],
        ], colWidths=[2.5 * inch, 2 * inch])
        summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        els += [summary, Spacer(1, 20), Paragraph("Incident Details", heading)]

        rows = [['Title', 'Severity', 'Status', 'Assigned To', 'Created']]
        for inc in incidents[:50]:
            rows.append([
                Paragraph(escape(inc.title[:60]), styles['Normal']),   # escape: titles may contain < >
                inc.severity.capitalize(),
                inc.status.replace('_', ' ').title(),
                Paragraph(escape(inc.assigned_to.email), styles['Normal']) if inc.assigned_to else 'Unassigned',
                inc.created_at.strftime('%Y-%m-%d'),
            ])
        if total > 50:
            els_note = Paragraph(f"Showing the 50 most recent of {total} incidents.", styles['Italic'])
        else:
            els_note = None
        table = Table(rows, colWidths=[2.2 * inch, 0.9 * inch, 1 * inch, 1.5 * inch, 1 * inch], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])]))
        els.append(table)
        if els_note:
            els += [Spacer(1, 8), els_note]
        doc.build(els)

        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = (
            f'attachment; filename="incident_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"')
        return resp