# chats/permissions.py
from rest_framework.permissions import BasePermission

class IsParticipantOfConversation(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()
