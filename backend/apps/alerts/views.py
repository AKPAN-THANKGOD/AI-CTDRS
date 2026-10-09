# LOCATION: backend/apps/alerts/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Alert
from .serializers import AlertSerializer
from apps.core.permissions import IsAdmin


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    filterset_fields = ['severity', 'status']
    search_fields = ['title', 'message']

    def get_queryset(self):
        qs = Alert.objects.select_related('threat', 'acknowledged_by').order_by('-created_at')
        # Dismissed alerts are hidden from the list unless asked for explicitly
        if self.action == 'list' and 'status' not in self.request.query_params:
            qs = qs.exclude(status='dismissed')
        return qs

    def get_permissions(self):
        # Raw create/edit/delete is admin only. Analysts use acknowledge/dismiss.
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=['status', 'acknowledged_by', 'acknowledged_at'])
        return Response({'status': 'alert acknowledged'})

    @action(detail=False, methods=['post'])
    def acknowledge_all(self, request):
        count = Alert.objects.filter(status='pending').update(
            status='acknowledged', acknowledged_by=request.user, acknowledged_at=timezone.now())
        return Response({'status': 'all alerts acknowledged', 'count': count})

    @action(detail=True, methods=['delete'])
    def dismiss(self, request, pk=None):
        """Soft-dismiss: keeps the record (audit trail) and uses the 'dismissed' status."""
        alert = self.get_object()
        alert.status = 'dismissed'
        alert.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)