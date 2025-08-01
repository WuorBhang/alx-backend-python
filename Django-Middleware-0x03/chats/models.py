from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError


class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    avatar = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    conversation_type = models.CharField(
        max_length=10,
        choices=[('direct', 'Direct Message'), ('group', 'Group Chat')],
        default='direct'
    )
    participants = models.ManyToManyField(User, through='ConversationParticipant')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_message_conversations')

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']

    def __str__(self):
        if self.name:
            return self.name
        participants = ", ".join([user.first_name for user in self.participants.all()[:3]])
        return f"Conversation between {participants}" + ("..." if self.participants.count() > 3 else "")


class ConversationParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    last_read_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'conversation_participants'
        unique_together = ['conversation', 'user']

    def clean(self):
        if self.conversation.conversation_type == 'direct' and self.conversation.participants.count() > 2:
            raise ValidationError("Direct conversations can only have 2 participants")

    def __str__(self):
        return f"{self.user.first_name} in {self.conversation}"


class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_body = models.TextField()
    message_type = models.CharField(
        max_length=10,
        choices=[('text', 'Text'), ('image', 'Image'), ('file', 'File'), ('system', 'System')],
        default='text'
    )
    file_url = models.URLField(blank=True, null=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_edited = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} in {self.conversation}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Conversation.objects.filter(
            conversation_id=self.conversation.conversation_id
        ).update(last_message=self)


class MessageReadStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_read_status'
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['user', 'read_at']),
        ]

    def __str__(self):
        return f"{self.user.first_name} read message {self.message.message_id}"