# chats/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ConversationParticipant, MessageReadStatus

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'content', 'message_type',
            'file_url', 'reply_to', 'is_edited', 'timestamp', 'updated_at', 'read_by'
        ]
        read_only_fields = ['id', 'sender', 'timestamp', 'updated_at', 'is_edited']

    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content,
                'sender': UserSerializer(obj.reply_to.sender).data
            }
        return None

    def get_read_by(self, obj):
        return [
            {
                'user': UserSerializer(status.user).data,
                'read_at': status.read_at
            }
            for status in obj.read_statuses.all()
        ]


class ConversationParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ConversationParticipant
        fields = ['id', 'user', 'joined_at', 'is_admin', 'last_read_message']


class ConversationSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(
        source='participants_details.all',
        many=True,
        read_only=True
    )
    last_message = MessageSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'name', 'conversation_type', 'participants',
            'created_by', 'created_at', 'updated_at', 'last_message', 'unread_count'
        ]

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        user = request.user
        try:
            participant = ConversationParticipant.objects.get(conversation=obj, user=user)
            if participant.last_read_message:
                return obj.messages.filter(timestamp__gt=participant.last_read_message.timestamp).count()
            return obj.messages.count()
        except ConversationParticipant.DoesNotExist:
            return 0


class CreateConversationSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    conversation_type = serializers.ChoiceField(
        choices=Conversation.CONVERSATION_TYPES,
        default='direct'
    )

    def validate_participant_ids(self, value):
        existing = User.objects.filter(id__in=value)
        if existing.count() != len(value):
            raise serializers.ValidationError("One or more users do not exist.")
        return value

    def validate(self, data):
        t = data.get('conversation_type')
        p = data.get('participant_ids', [])
        if t == 'direct' and len(p) != 1:
            raise serializers.ValidationError("Direct chat needs exactly 1 other user.")
        if t == 'group' and len(p) < 2:
            raise serializers.ValidationError("Group chat needs at least 2 participants.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        p_ids = validated_data.pop('participant_ids')

        # Check for existing direct chat
        if validated_data.get('conversation_type') == 'direct':
            other_id = p_ids[0]
            existing = Conversation.objects.filter(
                conversation_type='direct'
            ).annotate(
                pc=models.Count('participants_details')
            ).filter(
                pc=2,
                participants_details__user__in=[user.id, other_id]
            ).first()
            if existing:
                return existing

        # Create new
        conv = Conversation.objects.create(created_by=user, **validated_data)
        ConversationParticipant.objects.create(conversation=conv, user=user, is_admin=True)
        for pid in p_ids:
            u = User.objects.get(id=pid)
            ConversationParticipant.objects.create(conversation=conv, user=u, is_admin=False)

        return conv