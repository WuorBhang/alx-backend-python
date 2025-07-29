# messaging/views.py
from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404
from .models import Message

@cache_page(60)
def conversation_view(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    messages = Message.objects.filter(
        models.Q(sender=request.user, receiver=other_user) |
        models.Q(sender=other_user, receiver=request.user)
    ).select_related('sender', 'receiver').prefetch_related('messagehistory_set')
    
    return render(request, 'messaging/conversation.html', {
        'messages': messages,
        'other_user': other_user
    })