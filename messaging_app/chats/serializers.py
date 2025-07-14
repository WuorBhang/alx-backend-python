from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ConversationParticipant, MessageReadStatus

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_online', 'last_seen', 'avatar']
        read_only_fields = ['id', 'last_seen']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'message_type', 'file_url', 
                 'reply_to', 'is_edited', 'created_at', 'updated_at', 'read_by']
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at', 'is_edited']
    
    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content,
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
        fields = ['id', 'name', 'conversation_type', 'participants', 'created_by', 
                 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            return 0
        
        try:
            participant = ConversationParticipant.objects.get(conversation=obj, user=user)
            if participant.last_read_message:
                return Message.objects.filter(
                    conversation=obj,
                    created_at__gt=participant.last_read_message.created_at
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
        choices=Conversation.CONVERSATION_TYPES,
        default='direct'
    )
    
    def validate_participant_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one participant is required.")
        
        # Check if all users exist
        existing_users = User.objects.filter(id__in=value)
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
                participants__in=[user.id, other_user_id]
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
            participant = User.objects.get(id=participant_id)
            ConversationParticipant.objects.create(
                conversation=conversation,
                user=participant,
                is_admin=False
            )
        
        return conversation