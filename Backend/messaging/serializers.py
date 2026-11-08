from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from accounts.models import Store, User
from products.models import Product

from .models import Conversation, Message


# =============================================================================
# COMPACT USER / PRODUCT REPRESENTATIONS
# =============================================================================

class ChatUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    store = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "avatar", "is_active", "store"]
        read_only_fields = fields

    @extend_schema_field(
        serializers.DictField(
            child=serializers.CharField(), allow_null=True, default=None
        )
    )
    def get_store(self, obj):
        store = getattr(obj, "store", None)
        if not store:
            return None
        return {
            "name": store.name,
            "slug": store.slug,
            "verified": store.verified,
        }


class ChatProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "product_slug",
            "price",
            "state",
            "city",
            "image",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image(self, obj):
        request = self.context.get("request")
        first = obj.images.first()
        if not first:
            return None
        url = first.image.url
        return request.build_absolute_uri(url) if request else url


# =============================================================================
# MESSAGE
# =============================================================================

class MessageSerializer(serializers.ModelSerializer):
    sender = ChatUserSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id", "conversation", "sender", "body",
            "attachment_type", "attachment_url", "duration_ms",
            "read", "is_mine", "created_at",
        ]
        read_only_fields = ("id", "conversation", "sender", "read", "created_at")

    def validate(self, attrs):
        body = (attrs.get("body") or "").strip()
        attachment_type = attrs.get("attachment_type", "")
        attachment_url = attrs.get("attachment_url", "")
        # Text messages OR attachment messages are valid; empty everything is not.
        if not body and not attachment_type:
            raise serializers.ValidationError("Message cannot be empty.")
        if attachment_type and attachment_type not in dict(Message.ATTACHMENT_TYPE_CHOICES):
            raise serializers.ValidationError({"attachment_type": "Invalid attachment type."})
        if attachment_type and not attachment_url:
            raise serializers.ValidationError({"attachment_url": "Attachment URL is required."})
        return attrs

    @extend_schema_field(serializers.BooleanField(default=False))
    def get_is_mine(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.sender_id == request.user.id
        )

    def validate_body(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Message cannot be empty.")
        if len(value) > 4000:
            raise serializers.ValidationError(
                "Message is too long (maximum 4000 characters)."
            )
        return value


# =============================================================================
# CONVERSATION
# =============================================================================

class ConversationSerializer(serializers.ModelSerializer):
    product = ChatProductSerializer(read_only=True)
    buyer = ChatUserSerializer(read_only=True)
    seller = ChatUserSerializer(read_only=True)
    counterpart = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "product",
            "buyer",
            "seller",
            "counterpart",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    @extend_schema_field(ChatUserSerializer(allow_null=True))
    def get_counterpart(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        other = obj.other_participant(request.user)
        if not other:
            return None
        return ChatUserSerializer(other, context=self.context).data

    @extend_schema_field(MessageSerializer(allow_null=True))
    def get_last_message(self, obj):
        # Serves from the prefetched messages cache (see conversations_for);
        # falls back to a direct query only for single-object responses.
        cached = obj._prefetched_objects_cache.get("messages") if hasattr(obj, "_prefetched_objects_cache") else None
        if cached is not None:
            message = max(cached, key=lambda m: (m.created_at, m.pk)) if cached else None
        else:
            message = obj.last_message()
        if not message:
            return None
        return MessageSerializer(message, context=self.context).data

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_unread_count(self, obj):
        annotated = getattr(obj, "_annotated_unread_count", None)
        if annotated is not None:
            return annotated
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        return obj.unread_count_for(request.user)


class ConversationCreateSerializer(serializers.Serializer):
    """Start (or reuse) a conversation about a product and post a first message."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(active=True, sold=False)
    )
    message = serializers.CharField(max_length=4000)

    def validate_product(self, product):
        request = self.context["request"]
        if product.product_user_id == request.user.id:
            raise serializers.ValidationError(
                "You cannot start a conversation about your own listing."
            )
        return product

    def validate_message(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Message cannot be empty.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        product = validated_data["product"]

        conversation, _ = Conversation.objects.get_or_create(
            product=product,
            buyer=request.user,
            seller=product.product_user,
        )
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=validated_data["message"],
        )
        return conversation


class ConversationStartSerializer(ConversationCreateSerializer):
    """Alias kept for schema clarity on the start-chat endpoint."""
