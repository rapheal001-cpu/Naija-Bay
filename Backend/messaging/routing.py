from django.urls import re_path

from messaging.consumers import ChatConsumer, InboxConsumer

websocket_urlpatterns = [
    re_path(r"^ws/chat/$", InboxConsumer.as_asgi()),
    re_path(r"^ws/chat/(?P<conversation_id>[0-9]+)/$", ChatConsumer.as_asgi()),
]
