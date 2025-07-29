from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification


class MessagingTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass')
        self.user2 = User.objects.create_user(username='bob', password='pass')

    def test_message_creation_triggers_notification(self):
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hi Bob!"
        )
        self.assertTrue(Notification.objects.filter(message=msg).exists())

    def test_editing_message_creates_history(self):
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello"
        )
        msg.content = "Hello again!"
        msg.save()
        self.assertTrue(MessageHistory.objects.filter(message=msg).exists())
        self.assertEqual(MessageHistory.objects.first().old_content, "Hello")

    def test_unread_manager_filters_correctly(self):
        Message.objects.create(sender=self.user1, receiver=self.user2, content="Urgent", read=False)
        read_msg = Message.objects.create(sender=self.user1, receiver=self.user2, content="Old", read=True)

        unread = Message.unread.for_user(self.user2)
        self.assertEqual(unread.count(), 1)
        self.assertNotIn(read_msg, unread)