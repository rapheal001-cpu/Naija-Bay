"""Shared messaging logic used by both REST views and WebSocket consumers.

Keeping these rules in one place means the API and the socket enforce the same
block/clear/participant checks.
"""

from django.db.models import Q
from django.utils import timezone

from NaijaBay.realtime import safe_group_send

from .models import Conversation, ConversationUserState, UserBlock
from .serializers import ConversationSerializer


def user_inbox_group_name(user_id):
    return f"inbox_{user_id}"


def block_between(user, other_user):
    """The block record in either direction, or None."""
    if not user or not other_user:
        return None
    return UserBlock.objects.filter(
        Q(blocker=user, blocked_user=other_user)
        | Q(blocker=other_user, blocked_user=user)
    ).first()


def conversation_has_block(conversation):
    return bool(conversation and conversation.has_block())


def can_use_conversation(user, conversation):
    """Participant AND not blocked — the single access rule."""
    return bool(
        conversation
        and conversation.is_participant(user)
        and not conversation_has_block(conversation)
    )


def clear_conversation_for_user(conversation, user):
    """Hide a thread only for this user; other participants keep their history."""
    state, _created = ConversationUserState.objects.get_or_create(
        conversation=conversation, user=user
    )
    state.deleted_at = timezone.now()
    state.save(update_fields=["deleted_at"])


def conversation_payload_for(user, conversation):
    """Build a conversation payload *for one recipient*.

    Never reuse one payload across members: unread counts and last-message
    previews are private state.
    """
    return ConversationSerializer(conversation, context={"request": None}).data


def broadcast_inbox_event(user_ids, event, payload_builder):
    """Send an inbox event with a per-recipient payload.

    ``payload_builder(user_id)`` is called once per member so private fields
    cannot leak between participants.
    """
    for user_id in user_ids:
        safe_group_send(
            user_inbox_group_name(user_id),
            {
                "type": "chat.list.event",
                "event": event,
                "payload": payload_builder(user_id),
            },
        )
