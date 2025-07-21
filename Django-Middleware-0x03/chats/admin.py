from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, ConversationParticipant, Message, MessageReadStatus

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_online', 'last_seen']
    list_filter = ['is_online', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_online', 'last_seen', 'avatar')
        }),
    )

class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_id', 'name', 'conversation_type', 'created_by', 'created_at']
    list_filter = ['conversation_type', 'created_at']
    search_fields = ['name', 'created_by__username']
    inlines = [ConversationParticipantInline]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['created_by']  # Better for performance with many users

    # Remove filter_horizontal since you're using a through model
    # filter_horizontal = []  # Commented out since it's not needed

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'sender', 'conversation', 'message_body', 'message_type', 'sent_at']
    list_filter = ['message_type', 'sent_at', 'is_edited']
    search_fields = ['message_body', 'sender__username']
    readonly_fields = ['sent_at', 'updated_at']
    raw_id_fields = ['sender', 'conversation']  # Better for performance
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation')

@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['message__message_body', 'user__username']
    raw_id_fields = ['message', 'user']