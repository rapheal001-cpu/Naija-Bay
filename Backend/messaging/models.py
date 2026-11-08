from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import User


# =============================================================================
# CONVERSATION
# =============================================================================

class Conversation(models.Model):
    """A one-to-one chat thread between a buyer and a seller.

    A thread is normally anchored to a product so both parties keep the
    context of what is being discussed, but it may also be a direct message
    between two users (``product`` is ``NULL``).
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
        verbose_name=_("Product"),
        db_index=True,
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buying_conversations",
        verbose_name=_("Buyer"),
        db_index=True,
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="selling_conversations",
        verbose_name=_("Seller"),
        db_index=True,
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True, db_index=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "buyer", "seller"],
                name="unique_conversation_per_product",
            ),
            models.CheckConstraint(
                condition=~models.Q(buyer=models.F("seller")),
                name="prevent_self_conversation",
            ),
        ]
        indexes = [
            models.Index(fields=["buyer", "-updated_at"]),
            models.Index(fields=["seller", "-updated_at"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.buyer.username} <-> {self.seller.username}"

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def participant_ids(self):
        return {self.buyer_id, self.seller_id}

    def is_participant(self, user):
        return user.is_authenticated and user.id in self.participant_ids()

    def other_participant(self, user):
        if user.id == self.buyer_id:
            return self.seller
        if user.id == self.seller_id:
            return self.buyer
        return None

    def unread_count_for(self, user):
        return self.messages.filter(read=False).exclude(sender=user).count()

    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def touch(self):
        Conversation.objects.filter(pk=self.pk).update(updated_at=timezone.now())


# =============================================================================
# MESSAGE
# =============================================================================

class Message(models.Model):
    ATTACHMENT_TYPE_CHOICES = [
        ("image", "Image"),
        ("audio", "Voice Note"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Conversation"),
        db_index=True,
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name=_("Sender"),
        db_index=True,
    )
    body = models.TextField(_("Message"), blank=True)
    # Attachments (multi-image + voice notes share this WhatsApp-style shape).
    attachment_type = models.CharField(
        _("Attachment Type"), max_length=10, choices=ATTACHMENT_TYPE_CHOICES,
        blank=True, default="", db_index=True,
    )
    attachment_url = models.URLField(_("Attachment URL"), max_length=1000, blank=True)
    duration_ms = models.PositiveIntegerField(_("Duration (ms)"), default=0)
    read = models.BooleanField(_("Read"), default=False, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["conversation", "read"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.body[:40]}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            # Keep the thread at the top of both inboxes.
            Conversation.objects.filter(pk=self.conversation_id).update(
                updated_at=timezone.now()
            )

            # Notify the recipient (never the sender).
            from accounts.models import Notifications

            recipient_id = (
                self.conversation.seller_id
                if self.sender_id == self.conversation.buyer_id
                else self.conversation.buyer_id
            )
            if recipient_id and recipient_id != self.sender_id:
                product_name = (
                    self.conversation.product.product_name
                    if self.conversation.product_id
                    else "your listing"
                )
                Notifications.objects.create(
                    user_id=recipient_id,
                    notification_type="new_message",
                    message=(
                        f"New message from {self.sender.username} about "
                        f"{product_name}."
                    ),
                )
