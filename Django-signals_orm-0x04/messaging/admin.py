from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Message, Notification, Conversation, MessageHistory


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_at')
    search_fields = ('old_content',)
    
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Conversation)
#admin.site.register(MessageHistory)