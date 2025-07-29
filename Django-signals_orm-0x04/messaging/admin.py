# messaging/admin.py
from django.contrib import admin
from .models import Conversation, ConversationParticipant, Message, MessageReadStatus

admin.site.register(Conversation)
admin.site.register(ConversationParticipant)
admin.site.register(Message)
admin.site.register(MessageReadStatus)