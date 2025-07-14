from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, ConversationParticipant, MessageReadStatus
from .serializers import (
    ConversationSerializer, MessageSerializer, CreateConversationSerializer,
    UserSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'results': []})
        
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
        
        serializer = self.get_serializer(users, many=True)
        return Response({'results': serializer.data})
    
    @action(detail=False, methods=['patch'])
    def update_online_status(self, request):
        is_online = request.data.get('is_online', False)
        request.user.is_online = is_online
        request.user.save()
        return Response({'status': 'updated'})

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).select_related('created_by', 'last_message__sender').prefetch_related(
            'participants',
            'conversationparticipant_set__user'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateConversationSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the created conversation with full details
        response_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if conversation.conversation_type == 'direct':
            return Response({'error': 'Cannot add participants to direct conversations'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            participant, created = ConversationParticipant.objects.get_or_create(
                conversation=conversation,
                user=user,
                defaults={'is_admin': False}
            )
            
            if created:
                return Response({'message': 'Participant added successfully'})
            else:
                return Response({'message': 'User is already a participant'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if conversation.conversation_type == 'direct':
            return Response({'error': 'Cannot remove participants from direct conversations'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            participant = ConversationParticipant.objects.get(
                conversation=conversation,
                user_id=user_id
            )
            participant.delete()
            return Response({'message': 'Participant removed successfully'})
        except ConversationParticipant.DoesNotExist:
            return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        conversation = self.get_object()
        
        # Get the latest message in the conversation
        latest_message = conversation.messages.last()
        if not latest_message:
            return Response({'message': 'No messages to mark as read'})
        
        # Update the participant's last_read_message
        participant = get_object_or_404(
            ConversationParticipant,
            conversation=conversation,
            user=request.user
        )
        participant.last_read_message = latest_message
        participant.save()
        
        # Mark all messages as read
        unread_messages = Message.objects.filter(
            conversation=conversation,
            created_at__gt=participant.last_read_message.created_at if participant.last_read_message else None
        ).exclude(sender=request.user)
        
        for message in unread_messages:
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        return Response({'message': 'Conversation marked as read'})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            # Ensure user is participant in the conversation
            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                participants=self.request.user
            )
            return Message.objects.filter(conversation=conversation).select_related(
                'sender', 'reply_to__sender'
            ).prefetch_related('read_statuses__user')
        return Message.objects.none()
    
    def perform_create(self, serializer):
        conversation = get_object_or_404(
            Conversation,
            id=self.request.data.get('conversation'),
            participants=self.request.user
        )
        
        message = serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
        
        # Mark message as read by sender
        MessageReadStatus.objects.create(
            message=message,
            user=self.request.user
        )
        
        return message
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        
        # Ensure user is participant in the conversation
        if not message.conversation.participants.filter(id=request.user.id).exists():
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        if created:
            return Response({'message': 'Message marked as read'})
        else:
            return Response({'message': 'Message already read'})
    
    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        message = self.get_object()
        
        if message.sender != request.user:
            return Response({'error': 'Not authorized to edit this message'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message.content = content
        message.is_edited = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        
        if message.sender != request.user:
            return Response({'error': 'Not authorized to delete this message'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)