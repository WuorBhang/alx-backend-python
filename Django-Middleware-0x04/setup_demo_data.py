from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chats.models import Conversation, ConversationParticipant, Message

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo data for testing'
    
    def handle(self, *args, **options):
        # Create demo users
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                defaults={
                    'first_name': f'User{i+1}',
                    'last_name': 'Demo',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
            
        self.stdout.write(f'Created {len(users)} demo users')
        
        # Create demo conversations
        # Direct conversation
        direct_conv = Conversation.objects.create(
            conversation_type='direct',
            created_by=users[0]
        )
        ConversationParticipant.objects.create(conversation=direct_conv, user=users[0])
        ConversationParticipant.objects.create(conversation=direct_conv, user=users[1])
        
        # Group conversation
        group_conv = Conversation.objects.create(
            name='Team Chat',
            conversation_type='group',
            created_by=users[0]
        )
        for user in users[:4]:  # Add first 4 users to group
            ConversationParticipant.objects.create(
                conversation=group_conv, 
                user=user,
                is_admin=(user == users[0])
            )
        
        # Create some demo messages
        Message.objects.create(
            conversation=direct_conv,
            sender=users[0],
            content='Hello! How are you?'
        )
        Message.objects.create(
            conversation=direct_conv,
            sender=users[1],
            content='I am doing great! Thanks for asking.'
        )
        
        Message.objects.create(
            conversation=group_conv,
            sender=users[0],
            content='Welcome to the team chat!'
        )
        
        self.stdout.write(
            self.style.SUCCESS('Demo data created successfully!')
        )