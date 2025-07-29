# messaging/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

class SignalTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
    
    def test_notification_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello"
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().user, self.user2)
    
    def test_message_edit_logging(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original"
        )
        message.content = "Edited"
        message.save()
        self.assertEqual(MessageHistory.objects.count(), 1)
        self.assertEqual(message.edited, True)
    
    def test_user_deletion_cleanup(self):
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test"
        )
        self.user1.delete()
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 0)