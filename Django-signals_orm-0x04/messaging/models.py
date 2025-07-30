from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    topic = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )


    def __str__(self):
        return f"Conversation {self.pk}"


class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        return self.filter(receiver=user, read=False).only('id', 'sender', 'content', 'timestamp')


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey('messaging.Conversation', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, null=True, blank=True, related_name='edited_messages', on_delete=models.SET_NULL)
    read = models.BooleanField(default=False)  # ✅ new field

    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    
    objects = models.Manager()  # default
    unread = UnreadMessagesManager()  # ✅ custom manager

    def __str__(self):
        return f'{self.sender}: {self.content[:30]}'


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'History of Message ID {self.message.id} edited at {self.edited_at}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # receiver
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user} - Message ID {self.message.id}'
