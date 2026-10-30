from django.urls import path

from .views import (
    conversation_detail_view,
    conversation_list_create_view,
    conversation_read_view,
    message_list_create_view,
    unread_messages_count_view,
)

urlpatterns = [
    path("", conversation_list_create_view, name="conversation-list-create"),
    path("unread-count/", unread_messages_count_view, name="unread-messages-count"),
    path("<int:pk>/", conversation_detail_view, name="conversation-detail"),
    path("<int:pk>/messages/", message_list_create_view, name="message-list-create"),
    path("<int:pk>/read/", conversation_read_view, name="conversation-read"),
]
