from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity', 'status']
    search_fields = ['title', 'message']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response({'status': 'alert acknowledged'})
    
    @action(detail=False, methods=['post'])
    def acknowledge_all(self, request):
        pending = Alert.objects.filter(status='pending')
        pending.update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        return Response({'status': 'all alerts acknowledged'})
    
    @action(detail=True, methods=['delete'])
    def dismiss(self, request, pk=None):
        alert = self.get_object()
        alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)