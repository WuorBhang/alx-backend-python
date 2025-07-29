# messaging/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, MessageReadStatus


@receiver(post_save, sender=Message)
def mark_as_read_by_sender(sender, instance, created, **kwargs):
    if created:
        MessageReadStatus.objects.get_or_create(
            message=instance,
            user=instance.sender
        )