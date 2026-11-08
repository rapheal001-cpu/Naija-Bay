from decimal import Decimal

from django.test import TransactionTestCase
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

class ConversationListQueryCountTests(APITestCase):
    def test_conversation_list_uses_constant_queries(self):
        seller = User.objects.create_user(email="s2@example.com", username="s2", password="StrongPass123!")
        buyer = User.objects.create_user(email="b2@example.com", username="b2", password="StrongPass123!")
        for i in range(10):
            product = make_product(seller, name=f"Item {i}")
            conv = Conversation.objects.create(product=product, buyer=buyer, seller=seller)
            Message.objects.create(conversation=conv, sender=buyer, body=f"Question {i}")
            Message.objects.create(conversation=conv, sender=seller, body=f"Answer {i}", read=True)
        self.client.force_authenticate(buyer)
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse("conversation-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 10)
        self.assertLessEqual(len(ctx.captured_queries), 20, f"{len(ctx.captured_queries)} queries: N+1 regressed")


class ChatConsumerTests(TransactionTestCase):
    """Channels run DB access on worker threads; transactions would deadlock SQLite."""
    def setUp(self):
        self.seller = User.objects.create_user(email='s3@example.com', username='s3', password='StrongPass123!')
        self.buyer = User.objects.create_user(email='b3@example.com', username='b3', password='StrongPass123!')
        self.stranger = User.objects.create_user(email='x3@example.com', username='x3', password='StrongPass123!')
        self.product = make_product(self.seller)
        self.conv = Conversation.objects.create(buyer=self.buyer, seller=self.seller, product=self.product)
        Message.objects.create(conversation=self.conv, sender=self.buyer, body='Seed')

    def _app(self):
        from messaging.routing import websocket_urlpatterns
        from messaging.middleware import jwt_cookie_auth_middleware
        from channels.auth import AuthMiddlewareStack
        from channels.routing import URLRouter
        return jwt_cookie_auth_middleware(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))

    def test_unauthenticated_close_4401(self):
        import asyncio
        from channels.testing import WebsocketCommunicator
        async def run():
            communicator = WebsocketCommunicator(self._app(), f'/ws/chat/{self.conv.pk}/')
            return await communicator.connect()
        connected, close_code = asyncio.run(run())
        self.assertFalse(connected)
        self.assertEqual(close_code, 4401)

    def test_stranger_close_4404(self):
        import asyncio
        from channels.testing import WebsocketCommunicator
        from rest_framework_simplejwt.tokens import AccessToken
        token = str(AccessToken.for_user(self.stranger))
        async def run():
            communicator = WebsocketCommunicator(self._app(), f'/ws/chat/{self.conv.pk}/', headers=[(b'cookie', f'access={token}'.encode())])
            return await communicator.connect()
        connected, close_code = asyncio.run(run())
        self.assertFalse(connected)
        self.assertEqual(close_code, 4404)

    def test_participant_send_and_broadcast(self):
        import asyncio
        from channels.testing import WebsocketCommunicator
        from rest_framework_simplejwt.tokens import AccessToken
        buyer_token = str(AccessToken.for_user(self.buyer))
        seller_token = str(AccessToken.for_user(self.seller))
        async def run():
            buyer_ws = WebsocketCommunicator(self._app(), f'/ws/chat/{self.conv.pk}/', headers=[(b'cookie', f'access={buyer_token}'.encode())])
            seller_ws = WebsocketCommunicator(self._app(), f'/ws/chat/{self.conv.pk}/', headers=[(b'cookie', f'access={seller_token}'.encode())])
            a, _ = await buyer_ws.connect()
            b, _ = await seller_ws.connect()
            self.assertTrue(a and b)
            await buyer_ws.send_json_to({'type': 'message', 'body': 'Hello from buyer'})
            await seller_ws.receive_json_from(timeout=5)
            echoed = await buyer_ws.receive_json_from(timeout=5)
            await seller_ws.disconnect()
            await buyer_ws.disconnect()
            return echoed
        echoed = asyncio.run(run())
        self.assertEqual(echoed['type'], 'message')
        self.assertEqual(echoed['message']['body'], 'Hello from buyer')
        self.assertTrue(Message.objects.filter(conversation=self.conv, body='Hello from buyer').exists())
        self.assertEqual(self.conv.unread_count_for(self.seller), 2)

class AttachmentMessageTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(email='s9@example.com', username='s9', password='StrongPass123!')
        self.buyer = User.objects.create_user(email='b9@example.com', username='b9', password='StrongPass123!')
        self.product = make_product(self.seller)
        self.conv = Conversation.objects.create(buyer=self.buyer, seller=self.seller, product=self.product)
        self.client.force_authenticate(self.buyer)

    def test_send_image_attachment_via_rest(self):
        resp = self.client.post(
            f"/api/v1/messaging/{self.conv.pk}/messages/",
            {"body": "Check this out", "attachment_type": "image", "attachment_url": "https://cdn.example.com/a.jpg"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["attachment_type"], "image")
        self.assertEqual(resp.data["attachment_url"], "https://cdn.example.com/a.jpg")

    def test_attachment_without_url_rejected(self):
        resp = self.client.post(
            f"/api/v1/messaging/{self.conv.pk}/messages/",
            {"body": "", "attachment_type": "image"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_message_rejected(self):
        resp = self.client.post(
            f"/api/v1/messaging/{self.conv.pk}/messages/",
            {"body": ""},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
