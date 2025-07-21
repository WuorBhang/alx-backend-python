# chats/permissions.py
from rest_framework import permissions
from .models import Conversation, Message

class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        elif isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        return False

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Allows access only to the owner of the message or conversation participants.
    """
    def has_object_permission(self, request, view, obj):
        # For messages, check if user is sender or participant
        if isinstance(obj, Message):
            return (request.user == obj.sender) or (request.user in obj.conversation.participants.all())
        # For conversations, check if user is participant
        elif isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        return False
