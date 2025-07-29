from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ConversationParticipant, MessageReadStatus
from .serializers import MessageSerializer
from django.utils import timezone

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        
        # Check if user is participant in the conversation
        is_participant = await self.is_user_participant()
        if not is_participant:
            await self.close()
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        # Update user online status
        await self.update_user_online_status(True)
        
        await self.accept()
        
        # Notify others that user is online
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'user_status_update',
                'user_id': str(self.user.id),
                'is_online': True
            }
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'conversation_group_name'):
            # Leave conversation group
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
            
            # Update user online status
            await self.update_user_online_status(False)
            
            # Notify others that user is offline
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'user_status_update',
                    'user_id': str(self.user.id),
                    'is_online': False
                }
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'send_message':
                await self.handle_send_message(data)
            elif message_type == 'mark_as_read':
                await self.handle_mark_as_read(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'stop_typing':
                await self.handle_stop_typing(data)
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')
    
    async def handle_send_message(self, data):
        content = data.get('content', '').strip()
        reply_to_id = data.get('reply_to')
        message_type = data.get('message_type', 'text')
        
        if not content:
            await self.send_error('Message content cannot be empty')
            return
        
        # Create message
        message = await self.create_message(
            content=content,
            reply_to_id=reply_to_id,
            message_type=message_type
        )
        
        if message:
            # Serialize message
            serialized_message = await self.serialize_message(message)
            
            # Send to conversation group
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'new_message',
                    'message': serialized_message
                }
            )
    
    async def handle_mark_as_read(self, data):
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)
            
            # Notify others about read status
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'message_read',
                    'message_id': message_id,
                    'user_id': str(self.user.id)
                }
            )
    
    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'user_typing',
                'user_id': str(self.user.id),
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'is_typing': True
            }
        )
    
    async def handle_stop_typing(self, data):
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'user_typing',
                'user_id': str(self.user.id),
                'user_name': f"{self.user.first_name} {self.user.last_name}",
                'is_typing': False
            }
        )
    
    # Group message handlers
    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'user_id': event['user_id']
        }))
    
    async def user_typing(self, event):
        # Don't send typing status to the user who is typing
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))
    
    async def user_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status_update',
            'user_id': event['user_id'],
            'is_online': event['is_online']
        }))
    
    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    # Database operations
    @database_sync_to_async
    def is_user_participant(self):
        return ConversationParticipant.objects.filter(
            conversation_id=self.conversation_id,
            user=self.user
        ).exists()
    
    @database_sync_to_async
    def create_message(self, content, reply_to_id=None, message_type='text'):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id, conversation=conversation)
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
                reply_to=reply_to,
                message_type=message_type
            )
            
            # Mark as read by sender
            MessageReadStatus.objects.create(
                message=message,
                user=self.user
            )
            
            return message
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        # Create a mock request for serializer context
        request = HttpRequest()
        request.user = self.user
        
        serializer = MessageSerializer(message, context={'request': request})
        return serializer.data
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                conversation_id=self.conversation_id
            )
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=self.user
            )
            return True
        except Message.DoesNotExist:
            return False
    
    @database_sync_to_async
    def update_user_online_status(self, is_online):
        self.user.is_online = is_online
        self.user.last_seen = timezone.now()
        self.user.save()
"""

# WebSocket URL routing
# chats/routing.py
routing_content = """
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>[0-9a-f-]+)/
, consumers.ChatConsumer.as_asgi()),
]