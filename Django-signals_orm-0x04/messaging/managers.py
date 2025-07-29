# messaging/managers.py
from django.db import models

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)
    
    def for_user(self, user):
        return self.get_queryset().filter(receiver=user).only(
            'id', 'sender__username', 'content', 'timestamp'
        )