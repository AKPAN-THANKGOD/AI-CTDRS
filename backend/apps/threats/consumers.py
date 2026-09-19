import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class ThreatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from query string
        query_string = self.scope['query_string'].decode('utf-8')
        token_str = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token_str = param.split('=')[1]
                break
        
        # Authenticate user
        self.user = None
        if token_str:
            self.user = await self.get_user_from_token(token_str)
        
        if self.user and self.user.is_authenticated:
            self.room_group_name = 'threats_live'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"✅ WebSocket connected for user: {self.user.email}")
        else:
            print("❌ WebSocket connection rejected: Invalid or missing token")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        print("🔴 WebSocket disconnected")

    async def threat_detected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'threat_detected',
            'threat': event['threat']
        }))

    @database_sync_to_async
    def get_user_from_token(self, token_str):
        try:
            valid_token = AccessToken(token_str)
            user_id = valid_token['user_id']
            return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None


def broadcast_threat(threat_data):
    """Synchronously broadcast threat to all connected WebSocket clients."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'threats_live',
        {
            'type': 'threat_detected',
            'threat': threat_data
        }
    )