# chats/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q, Count as models_Count
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, ConversationParticipant, MessageReadStatus
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
    CreateConversationSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '')
        if len(q) < 2:
            return Response({'results': []})
        users = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        ).exclude(id=request.user.id)[:10]
        return Response({'results': UserSerializer(users, many=True).data})

    @action(detail=False, methods=['patch'])
    def update_online_status(self, request):
        # Optional: add is_online field later
        return Response({'status': 'not_implemented'})


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants_details__user=self.request.user
        ).select_related('created_by').prefetch_related(
            'participants_details__user',
            'messages__sender'
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateConversationSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        return Response(
            ConversationSerializer(conversation, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conv = self.get_object()
        if conv.conversation_type == 'direct':
            return Response({'error': 'Cannot add to direct'}, status=400)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)
        user = get_object_or_404(User, id=user_id)
        _, created = ConversationParticipant.objects.get_or_create(
            conversation=conv, user=user
        )
        msg = 'Added' if created else 'Already participant'
        return Response({'message': msg})

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        conv = self.get_object()
        if conv.conversation_type == 'direct':
            return Response({'error': 'Cannot remove from direct'}, status=400)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)
        participant = get_object_or_404(ConversationParticipant, conversation=conv, user_id=user_id)
        participant.delete()
        return Response({'message': 'Removed'})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        conv = self.get_object()
        latest = conv.messages.last()
        if not latest:
            return Response({'message': 'No messages'})
        participant = get_object_or_404(ConversationParticipant, conversation=conv, user=request.user)
        participant.last_read_message = latest
        participant.save()
        return Response({'message': 'Marked as read'})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cid = self.request.query_params.get('conversation')
        if cid:
            return Message.objects.filter(conversation_id=cid).select_related('sender', 'reply_to__sender')
        return Message.objects.none()

    def perform_create(self, serializer):
        cid = self.request.data.get('conversation')
        conv = get_object_or_404(Conversation, id=cid)
        if not conv.participants_details.filter(user=self.request.user).exists():
            raise PermissionDenied()
        msg = serializer.save(sender=self.request.user, conversation=conv)
        MessageReadStatus.objects.get_or_create(message=msg, user=self.request.user)
        return msg

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        msg = self.get_object()
        MessageReadStatus.objects.get_or_create(message=msg, user=request.user)
        return Response({'message': 'Read'})

    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        msg = self.get_object()
        if msg.sender != request.user:
            return Response({'error': 'No permission'}, status=403)
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content required'}, status=400)
        msg.content = content
        msg.is_edited = True
        msg.save()
        return Response(MessageSerializer(msg).data)

    def destroy(self, request, *args, **kwargs):
        msg = self.get_object()
        if msg.sender != request.user:
            return Response({'error': 'No permission'}, status=403)
        return super().destroy(request, *args, **kwargs)