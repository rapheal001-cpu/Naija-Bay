from django.urls import path

from .views import (
    conversation_clear_view,
    conversation_detail_view,
    conversation_list_create_view,
    conversation_read_view,
    message_list_create_view,
    unread_messages_count_view,
    user_block_detail_view,
    user_block_list_create_view,
)

urlpatterns = [
    path("", conversation_list_create_view, name="conversation-list-create"),
    path("unread-count/", unread_messages_count_view, name="unread-messages-count"),
    path("<int:pk>/", conversation_detail_view, name="conversation-detail"),
    path("<int:pk>/messages/", message_list_create_view, name="message-list-create"),
    path("<int:pk>/read/", conversation_read_view, name="conversation-read"),
    path("<int:pk>/clear/", conversation_clear_view, name="conversation-clear"),
    path("blocks/", user_block_list_create_view, name="user-block-list"),
    path("blocks/<int:pk>/", user_block_detail_view, name="user-block-detail"),
]
