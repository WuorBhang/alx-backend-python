# chats/permissions.py
from rest_framework import permissions
from .models import Conversation, Message

class IsAuthenticatedParticipant(permissions.BasePermission):
    """
    Comprehensive permission class that:
    1. Requires authentication for all requests
    2. Checks participant status for object access
    3. Handles different HTTP methods explicitly
    4. Provides owner checks for message modifications
    """

    def has_permission(self, request, view):
        # First and foremost - require authentication
        if not request.user.is_authenticated:
            return False

        # Allow POST requests to create new conversations/messages
        if request.method == 'POST':
            return True

        # For other methods, defer to object-level permissions
        return True

    def has_object_permission(self, request, view, obj):
        # Double-check authentication (defensive programming)
        if not request.user.is_authenticated:
            return False

        # Check participant status
        is_participant = self._is_participant(request.user, obj)

        # SAFE_METHODS (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return is_participant

        # Modification methods (PUT, PATCH, DELETE)
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            # For messages, require ownership AND participant status
            if isinstance(obj, Message):
                return (request.user == obj.sender) and is_participant
            # For conversations, just require participant status
            return is_participant

        return False

    def _is_participant(self, user, obj):
        """Helper method to check participant status"""
        if isinstance(obj, Conversation):
            return user in obj.participants.all()
        elif isinstance(obj, Message):
            return user in obj.conversation.participants.all()
        return False


# Aliases for backward compatibility and specific use cases
IsParticipant = IsAuthenticatedParticipant  # Simple participant check
IsOwnerOrParticipant = IsAuthenticatedParticipant  # Includes owner checks for messages
