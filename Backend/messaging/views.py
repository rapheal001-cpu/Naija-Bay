from django.db.models import Count, Q
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from NaijaBay.queryset_helper import with_conversation_context

from accounts.models import Notifications
from products.models import Product
from NaijaBay.pagination import StandardPagination

from .models import Conversation, ConversationUserState, Message, UserBlock
from .services import clear_conversation_for_user, user_inbox_group_name
from NaijaBay.realtime import safe_group_send
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    ConversationStartSerializer,
    MessageSerializer,
    UserBlockCreateSerializer,
    UserBlockSerializer,
)



def conversations_for(user):
    """Conversations the user takes part in, with the unread count annotated.

    The last message is read from the prefetched messages cache (one batch
    query) and the unread count is a single annotated COUNT — no per-row
    queries during serialization.
    """
    cleared_ids = ConversationUserState.objects.filter(
        user=user, deleted_at__isnull=False
    ).values_list("conversation_id", flat=True)
    blocked_ids = Conversation.objects.filter(
        Q(buyer=user, seller__blocks_received__blocker=user)
        | Q(seller=user, buyer__blocks_received__blocker=user)
    ).values_list("pk", flat=True)
    return with_conversation_context(
        Conversation.objects.filter(Q(buyer=user) | Q(seller=user))
        .exclude(pk__in=cleared_ids)
        .exclude(pk__in=blocked_ids)
        .order_by("-updated_at"),
        user,
    )


def get_conversation_or_404(user, conversation_id):
    return get_object_or_404(conversations_for(user), pk=conversation_id)



@extend_schema_view(
    get=extend_schema(tags=["Messaging"], operation_id="List Conversations"),
    post=extend_schema(
        tags=["Messaging"],
        operation_id="Start Conversation",
        request=ConversationStartSerializer,
        responses={201: ConversationSerializer},
    ),
)
class ConversationListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationStartSerializer
        return ConversationSerializer

    def get_queryset(self):
        return conversations_for(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        output = ConversationSerializer(
            conversation, context={"request": request}
        )
        return Response(output.data, status=status.HTTP_201_CREATED)


conversation_list_create_view = ConversationListCreateAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Messaging"], operation_id="Conversation Detail")
)
class ConversationDetailAPIView(RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_conversation_or_404(self.request.user, self.kwargs["pk"])


conversation_detail_view = ConversationDetailAPIView.as_view()



@extend_schema_view(
    get=extend_schema(tags=["Messaging"], operation_id="List Messages"),
    post=extend_schema(
        tags=["Messaging"],
        operation_id="Send Message",
        request=MessageSerializer,
        responses={201: MessageSerializer},
    ),
)
class MessageListCreateAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_conversation(self):
        return get_conversation_or_404(self.request.user, self.kwargs["pk"])

    def get_queryset(self):
        return self.get_conversation().messages.select_related("sender")

    def perform_create(self, serializer):
        conversation = self.get_conversation()
        message = serializer.save(
            conversation=conversation,
            sender=self.request.user,
            attachment_type=serializer.validated_data.get("attachment_type", ""),
            attachment_url=serializer.validated_data.get("attachment_url", ""),
            duration_ms=serializer.validated_data.get("duration_ms", 0),
        )
        conversation.messages.filter(read=False).exclude(
            sender=self.request.user
        ).update(read=True)
        return message

    def create(self, request, *args, **kwargs):
        conversation = self.get_conversation()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(
            conversation=conversation,
            sender=request.user,
            attachment_type=serializer.validated_data.get("attachment_type", ""),
            attachment_url=serializer.validated_data.get("attachment_url", ""),
            duration_ms=serializer.validated_data.get("duration_ms", 0),
        )
        conversation.messages.filter(read=False).exclude(sender=request.user).update(
            read=True
        )

        output = MessageSerializer(message, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


message_list_create_view = MessageListCreateAPIView.as_view()


@extend_schema_view(
    post=extend_schema(tags=["Messaging"], operation_id="Mark Conversation Read")
)
class ConversationReadAPIView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        conversation = get_conversation_or_404(request.user, pk)
        updated = conversation.messages.filter(read=False).exclude(
            sender=request.user
        ).update(read=True)

        return Response(
            {
                "detail": "Conversation marked as read.",
                "messages_read": updated,
                "unread_count": conversation.unread_count_for(request.user),
            },
            status=status.HTTP_200_OK,
        )


conversation_read_view = ConversationReadAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Messaging"], operation_id="Unread Messages Count")
)
class UnreadMessagesCountAPIView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Message.objects.filter(
            Q(conversation__buyer=request.user) | Q(conversation__seller=request.user),
            read=False,
        ).exclude(sender=request.user).count()

        return Response(
            {
                "unread_messages": count,
                "unread_notifications": Notifications.objects.filter(
                    user=request.user, read=False
                ).count(),
            },
            status=status.HTTP_200_OK,
        )


unread_messages_count_view = UnreadMessagesCountAPIView.as_view()



@extend_schema_view(
    get=extend_schema(tags=["Messaging"], operation_id="List blocked users"),
    post=extend_schema(
        tags=["Messaging"], operation_id="Block user",
        request=UserBlockCreateSerializer, responses={201: UserBlockSerializer},
    ),
)
class UserBlockListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        return UserBlockCreateSerializer if self.request.method == "POST" else UserBlockSerializer

    def get_queryset(self):
        return UserBlock.objects.filter(blocker=self.request.user).select_related("blocked_user")

    def create(self, request, *args, **kwargs):
        serializer = UserBlockCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        other_id = serializer.validated_data["user"]
        block, _created = UserBlock.objects.get_or_create(
            blocker=request.user, blocked_user_id=other_id
        )

        for conversation in Conversation.objects.filter(
            Q(buyer=request.user, seller_id=other_id)
            | Q(seller=request.user, buyer_id=other_id)
        ):
            safe_group_send(
                f"chat_{conversation.pk}",
                {"type": "chat.event", "event": "conversation_blocked", "payload": {}},
            )
            for member_id in conversation.participant_ids():
                safe_group_send(
                    user_inbox_group_name(member_id),
                    {
                        "type": "chat.list.event",
                        "event": "conversation_blocked",
                        "payload": {"conversation_id": conversation.pk},
                    },
                )

        return Response(UserBlockSerializer(block).data, status=status.HTTP_201_CREATED)


user_block_list_create_view = UserBlockListCreateAPIView.as_view()


@extend_schema_view(
    delete=extend_schema(tags=["Messaging"], operation_id="Unblock user")
)
class UserBlockDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        block = get_object_or_404(UserBlock, pk=pk, blocker=request.user)
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


user_block_detail_view = UserBlockDetailAPIView.as_view()



@extend_schema_view(
    post=extend_schema(tags=["Messaging"], operation_id="Clear conversation for me")
)
class ConversationClearAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        conversation = get_conversation_or_404(request.user, pk)
        clear_conversation_for_user(conversation, request.user)
        safe_group_send(
            user_inbox_group_name(request.user.pk),
            {
                "type": "chat.list.event",
                "event": "conversation_cleared",
                "payload": {"conversation_id": conversation.pk},
            },
        )
        return Response(
            {"detail": "Conversation cleared.", "conversation_id": conversation.pk},
            status=status.HTTP_200_OK,
        )


conversation_clear_view = ConversationClearAPIView.as_view()
