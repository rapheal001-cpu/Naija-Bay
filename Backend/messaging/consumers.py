"""WebSocket consumers for marketplace chat (SkillStream pattern).

Protocol (JSON, all messages are objects):

Room socket ``ws/chat/<conversation_id>/``:
  client → server
    {"type": "message", "body": "..."}     send a message (max 4000 chars)
    {"type": "typing", "is_typing": bool}  typing indicator
    {"type": "read"}                       mark thread read
  server → client
    {"type": "message", "message": {...}}  new/rest materialized message
    {"type": "typing", ...}
    {"type": "error", "detail": "..."}

Inbox socket ``ws/chat/``:
  server → client
    {"type": "message", "conversation_id": n, "message": {...}}
    {"type": "unread", "conversation_id": n, "unread_count": n}

Close codes: 4401 unauthenticated, 4404 no access to the conversation,
4403 access revoked mid-session, 1013 channel layer unavailable.
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from NaijaBay.realtime import (
    async_safe_group_send,
    safe_group_add,
    safe_group_discard,
)

from .models import Conversation, Message
from .serializers import MessageSerializer


def chat_group_name(conversation_id):
    return f"chat_{conversation_id}"


def user_inbox_group_name(user_id):
    return f"inbox_{user_id}"


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """Live chat room for one conversation."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        if not await self.is_participant():
            await self.close(code=4404)
            return

        self.room_group_name = chat_group_name(self.conversation_id)
        if not await safe_group_add(self.channel_layer, self.room_group_name, self.channel_name):
            self.room_group_name = None
            await self.close(code=1013)
            return
        await self.accept()

    async def disconnect(self, close_code):
        room_group_name = getattr(self, "room_group_name", None)
        if room_group_name:
            await safe_group_discard(self.channel_layer, room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if not isinstance(content, dict):
            await self.send_json({"type": "error", "detail": "Unknown chat event."})
            return

        event_type = content.get("type")
        if event_type == "message":
            if not await self.is_participant():
                await self.close(code=4403)
                return
            body = (content.get("body") or "").strip()
            attachment_type = content.get("attachment_type") or ""
            attachment_url = (content.get("attachment_url") or "").strip()
            duration_ms = content.get("duration_ms") or 0
            if body and len(body) > 4000:
                await self.send_json({"type": "error", "detail": "Message is too long (maximum 4000 characters)."})
                return
            if not body and not attachment_type:
                await self.send_json({"type": "error", "detail": "Message must contain text or an attachment."})
                return
            if attachment_type and not attachment_url:
                await self.send_json({"type": "error", "detail": "Attachment URL is required."})
                return
            payload = await self.save_message(body, attachment_type, attachment_url, duration_ms)
            if payload is None:
                await self.close(code=4403)
                return
            await self.broadcast(room_extra={"message": payload})
            return

        if event_type == "typing":
            if await self.is_participant():
                await async_safe_group_send(
                    self.channel_layer,
                    self.room_group_name,
                    {
                        "type": "chat.event",
                        "event": "typing",
                        "payload": {
                            "user_id": self.scope["user"].pk,
                            "username": self.scope["user"].username,
                            "is_typing": bool(content.get("is_typing")),
                        },
                    },
                )
            return

        if event_type == "read":
            await self.mark_read()
            return

        await self.send_json({"type": "error", "detail": "Unknown chat event."})

    async def chat_event(self, event):
        await self.send_json({"type": event["event"], **event.get("payload", {})})

    async def broadcast(self, room_extra=None):
        room_extra = room_extra or {}
        payload = {
            "conversation_id": self.conversation_id,
            **room_extra,
        }
        # Room participants get the live message.
        await async_safe_group_send(
            self.channel_layer,
            self.room_group_name,
            {"type": "chat.event", "event": "message", "payload": payload},
        )
        # Both inboxes get presence + unread pushes.
        for member_id in await self.other_member_ids():
            await async_safe_group_send(
                self.channel_layer,
                user_inbox_group_name(member_id),
                {
                    "type": "chat.list.event",
                    "event": "message",
                    "payload": {
                        "conversation_id": self.conversation_id,
                        "message": payload.get("message"),
                    },
                },
            )

    @database_sync_to_async
    def other_member_ids(self):
        conversation = Conversation.objects.filter(pk=self.conversation_id).first()
        if conversation is None:
            return []
        other = conversation.other_participant(self.scope["user"])
        return [other.pk] if other else []

    @database_sync_to_async
    def is_participant(self):
        conversation = Conversation.objects.filter(pk=self.conversation_id).first()
        return bool(conversation and conversation.is_participant(self.scope["user"]))

    @database_sync_to_async
    def save_message(self, body, attachment_type="", attachment_url="", duration_ms=0):
        conversation = Conversation.objects.filter(pk=self.conversation_id).first()
        if conversation is None or not conversation.is_participant(self.scope["user"]):
            return None
        # Message.save() notifies the recipient (existing Signal-free logic
        # in the model) — no extra paths to keep in sync.
        message = Message.objects.create(
            conversation=conversation,
            sender=self.scope["user"],
            body=body,
            attachment_type=attachment_type,
            attachment_url=attachment_url,
            duration_ms=duration_ms,
        )
        conversation.touch()
        return MessageSerializer(message).data

    @database_sync_to_async
    def mark_read(self):
        conversation = Conversation.objects.filter(pk=self.conversation_id).first()
        if conversation is None:
            return False
        conversation.messages.filter(read=False).exclude(sender=self.scope["user"]).update(read=True)
        return True


class InboxConsumer(AsyncJsonWebsocketConsumer):
    """Per-user inbox push socket (new messages + unread counts)."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group_name = user_inbox_group_name(user.pk)
        if not await safe_group_add(self.channel_layer, self.group_name, self.channel_name):
            self.group_name = None
            await self.close(code=1013)
            return
        await self.accept()

    async def disconnect(self, close_code):
        group_name = getattr(self, "group_name", None)
        if group_name:
            await safe_group_discard(self.channel_layer, group_name, self.channel_name)

    async def chat_list_event(self, event):
        await self.send_json({"type": event["event"], **event.get("payload", {})})
