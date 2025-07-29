from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message


@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).select_related('sender')
    return render(request, 'inbox.html', {'messages': messages})