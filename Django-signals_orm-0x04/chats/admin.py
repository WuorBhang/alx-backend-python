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
    list_display = ['id', 'name', 'conversation_type', 'created_by', 'created_at']
    list_filter = ['conversation_type', 'created_at']
    search_fields = ['name', 'created_by__username']
    inlines = [ConversationParticipantInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'content', 'message_type', 'created_at']
    list_filter = ['message_type', 'created_at', 'is_edited']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation')

@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['message__content', 'user__username']