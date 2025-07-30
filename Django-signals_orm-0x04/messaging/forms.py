# messaging/forms.py

from django import forms
from .models import Message

class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(MessageReplyForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'placeholder': 'Type your reply here...'})
