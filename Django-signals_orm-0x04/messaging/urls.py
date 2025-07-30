from django.urls import path
from . import views
from .views import conversation_detail, reply_to_message, unread_messages_view
from .views import conversation_detail_view #unread_messages

urlpatterns = [
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('delete_account/', views.delete_user, name='delete_account'),
    path('conversations/<int:conversation_id>/', conversation_detail, name='conversation_detail'),
    path('conversations/<int:conversation_id>/reply/<int:parent_message_id>/', reply_to_message, name='reply_to_message'),
    #path('messages/unread/', unread_messages, name='unread_messages'), 
    path('conversation/<int:conversation_id>/', conversation_detail_view, name='conversation_detail'),
    #path('messages/unread/', unread_messages_view, name='unread_messages'),
]
    #path('messages/<int:pk>/', views.message_detail, name='message_detail'),
#]
