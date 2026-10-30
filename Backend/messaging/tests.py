from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Notifications, User
from messaging.models import Conversation, Message
from products.models import Product


def make_product(owner, name="Chat Product"):
    return Product.objects.create(
        product_user=owner,
        product_name=name,
        description="A product used to exercise the messaging endpoints.",
        price=Decimal("25000.00"),
        category="phones_tablets",
        sub_category="mobile_phones",
        condition="used",
        color="#333333",
        quantity=1,
        state="lagos",
        city="ikeja",
        contact_methods=["whatsapp"],
        contact_number="+2348012345678",
    )


class MessagingAPITests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="seller@example.com",
            username="seller",
            password="StrongPass123!",
        )
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            username="buyer",
            password="StrongPass123!",
        )
        self.stranger = User.objects.create_user(
            email="stranger@example.com",
            username="stranger",
            password="StrongPass123!",
        )
        self.product = make_product(self.seller)

    def start_conversation(self):
        self.client.force_authenticate(self.buyer)
        return self.client.post(
            reverse("conversation-list-create"),
            {"product": self.product.id, "message": "Is this still available?"},
            format="json",
        )

    def test_start_conversation_creates_thread_and_notifies_seller(self):
        response = self.start_conversation()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation = Conversation.objects.get(
            product=self.product, buyer=self.buyer, seller=self.seller
        )
        self.assertEqual(conversation.messages.count(), 1)
        self.assertTrue(
            Notifications.objects.filter(
                user=self.seller, notification_type="new_message"
            ).exists()
        )

    def test_starting_twice_reuses_conversation(self):
        self.start_conversation()
        response = self.start_conversation()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)

    def test_cannot_start_conversation_on_own_product(self):
        self.client.force_authenticate(self.seller)

        response = self.client.post(
            reverse("conversation-list-create"),
            {"product": self.product.id, "message": "Talking to myself"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_list_is_scoped_to_participant(self):
        self.start_conversation()

        self.client.force_authenticate(self.buyer)
        response = self.client.get(reverse("conversation-list-create"))
        self.assertEqual(response.data["count"], 1)

        self.client.force_authenticate(self.stranger)
        response = self.client.get(reverse("conversation-list-create"))
        self.assertEqual(response.data["count"], 0)

    def test_send_and_read_messages(self):
        response = self.start_conversation()
        conversation_id = response.data["id"]

        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("message-list-create", kwargs={"pk": conversation_id}),
            {"body": "Yes, it is available."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["read"])

        self.client.force_authenticate(self.buyer)
        response = self.client.get(reverse("conversation-list-create"))
        self.assertEqual(response.data["results"][0]["unread_count"], 1)

        response = self.client.post(
            reverse("conversation-read", kwargs={"pk": conversation_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["messages_read"], 1)

        response = self.client.get(reverse("conversation-list-create"))
        self.assertEqual(response.data["results"][0]["unread_count"], 0)

    def test_non_participant_cannot_read_conversation(self):
        response = self.start_conversation()
        conversation_id = response.data["id"]

        self.client.force_authenticate(self.stranger)
        response = self.client.get(
            reverse("message-list-create", kwargs={"pk": conversation_id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_message_is_rejected(self):
        response = self.start_conversation()
        conversation_id = response.data["id"]

        self.client.force_authenticate(self.buyer)
        response = self.client.post(
            reverse("message-list-create", kwargs={"pk": conversation_id}),
            {"body": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unread_count_endpoint(self):
        self.start_conversation()

        self.client.force_authenticate(self.seller)
        response = self.client.get(reverse("unread-messages-count"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unread_messages"], 1)
        self.assertEqual(
            response.data["unread_notifications"],
            Notifications.objects.filter(user=self.seller, read=False).count(),
        )

    def test_messaging_requires_authentication(self):
        response = self.client.get(reverse("conversation-list-create"))
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
