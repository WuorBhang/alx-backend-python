from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ConversationParticipant, MessageReadStatus
from django.db import models

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 
                 'is_online', 'last_seen', 'avatar']
        read_only_fields = ['user_id', 'last_seen']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 
                 'message_type', 'file_url', 'reply_to', 'is_edited', 
                 'sent_at', 'updated_at', 'read_by']
        read_only_fields = ['message_id', 'sender', 'sent_at', 'updated_at', 'is_edited']
    
    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'message_id': obj.reply_to.message_id,
                'message_body': obj.reply_to.message_body,
                'sender': UserSerializer(obj.reply_to.sender).data
            }
        return None
    
    def get_read_by(self, obj):
        read_statuses = MessageReadStatus.objects.filter(message=obj).select_related('user')
        return [
            {
                'user': UserSerializer(status.user).data,
                'read_at': status.read_at
            }
            for status in read_statuses
        ]

class ConversationParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ConversationParticipant
        fields = ['id', 'user', 'joined_at', 'is_admin', 'last_read_message']

class ConversationSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(
        source='conversationparticipant_set', 
        many=True, 
        read_only=True
    )
    last_message = MessageSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'name', 'conversation_type', 'participants', 
                 'created_by', 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['conversation_id', 'created_by', 'created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            return 0
        
        try:
            participant = ConversationParticipant.objects.get(conversation=obj, user=user)
            if participant.last_read_message:
                return Message.objects.filter(
                    conversation=obj,
                    sent_at__gt=participant.last_read_message.sent_at
                ).count()
            else:
                return Message.objects.filter(conversation=obj).count()
        except ConversationParticipant.DoesNotExist:
            return 0

class CreateConversationSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    conversation_type = serializers.ChoiceField(
        choices=[('direct', 'Direct Message'), ('group', 'Group Chat')],
        default='direct'
    )
    
    def validate_participant_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one participant is required.")
        
        existing_users = User.objects.filter(user_id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("Some users do not exist.")
        
        return value
    
    def validate(self, data):
        if data.get('conversation_type') == 'direct' and len(data.get('participant_ids', [])) != 1:
            raise serializers.ValidationError("Direct conversations must have exactly one other participant.")
        
        if data.get('conversation_type') == 'group' and len(data.get('participant_ids', [])) < 2:
            raise serializers.ValidationError("Group conversations must have at least 2 participants.")
        
        return data
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        user = self.context['request'].user
        
        # For direct messages, check if conversation already exists
        if validated_data.get('conversation_type') == 'direct':
            other_user_id = participant_ids[0]
            existing_conversation = Conversation.objects.filter(
                conversation_type='direct',
                participants__in=[user.user_id, other_user_id]
            ).annotate(
                participant_count=models.Count('participants')
            ).filter(participant_count=2).first()
            
            if existing_conversation:
                return existing_conversation
        
        # Create new conversation
        conversation = Conversation.objects.create(
            created_by=user,
            **validated_data
        )
        
        # Add creator as participant
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=user,
            is_admin=True
        )
        
        # Add other participants
        for participant_id in participant_ids:
            participant = User.objects.get(user_id=participant_id)
            ConversationParticipant.objects.create(
                conversation=conversation,
                user=participant,
                is_admin=False
            )
        
        return conversation