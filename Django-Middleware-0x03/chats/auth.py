# messaging_app/chats/auth.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Conversation

class JWTAuthWithParticipantCheck(JWTAuthentication):
    """
    Custom JWT authentication that also verifies the user is a conversation participant.
    """
    
    def authenticate(self, request):
        # First authenticate via JWT
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is None:
            return None
            
        user, token = user_auth_tuple
        
        # For conversation-specific endpoints, verify participant status
        if 'conversation_id' in request.resolver_match.kwargs:
            conversation_id = request.resolver_match.kwargs['conversation_id']
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                if user not in conversation.participants.all():
                    raise PermissionDenied("You are not a participant in this conversation")
            except Conversation.DoesNotExist:
                raise PermissionDenied("Conversation does not exist")
        
        return (user, token)


class IsParticipant(IsAuthenticated):
    """
    Permission class that checks if user is a conversation participant.
    Works in conjunction with JWTAuthWithParticipantCheck.
    """
    
    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
            
        # For Message objects
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
            
        return False


def get_auth_header(request):
    """
    Helper function to extract JWT token from request header
    """
    header = request.META.get('HTTP_AUTHORIZATION', '')
    if header.startswith('Bearer '):
        return header.split(' ')[1]
    return None
