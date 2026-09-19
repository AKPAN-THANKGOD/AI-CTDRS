from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/threats/$', consumers.ThreatConsumer.as_asgi()),
]