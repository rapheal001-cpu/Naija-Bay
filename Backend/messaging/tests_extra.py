"""Tests for messaging block and per-user clear behaviour."""

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from messaging.models import Conversation, Message, UserBlock
from products.models import Product


class MessagingSafetyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user("m-buyer@m.test", "mbuyer", "TestPass123!")
        cls.seller = User.objects.create_user("m-seller@m.test", "mseller", "TestPass123!")
        cls.product = Product.objects.create(
            product_user=cls.seller,
            product_name="Messaging test item",
            description="test",
            price=Decimal("10000.00"),
            category="phones_tablets",
            sub_category="mobile_phones",
            condition="used",
            color="black",
            quantity=1,
            state="lagos",
            city="ikeja",
            contact_methods=["whatsapp"],
            contact_number="+2348012345678",
        )

    def setUp(self):
        self.client = APIClient()

    def _start(self):
        self.client.force_authenticate(user=self.buyer)
        return self.client.post(
            "/api/v1/messaging/",
            {"product": self.product.pk, "message": "Hello, is this available?"},
            format="json",
        )

    def test_block_and_unblock(self):
        self.client.force_authenticate(user=self.buyer)
        r = self.client.post("/api/v1/messaging/blocks/", {"user": self.seller.pk}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        block_id = r.data["id"]
        self.assertTrue(UserBlock.objects.filter(blocker=self.buyer, blocked_user=self.seller).exists())
        r = self.client.delete(f"/api/v1/messaging/blocks/{block_id}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(UserBlock.objects.exists())

    def test_cannot_block_self(self):
        self.client.force_authenticate(user=self.buyer)
        r = self.client.post("/api/v1/messaging/blocks/", {"user": self.buyer.pk}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_block_prevents_starting_conversation(self):
        self.client.force_authenticate(user=self.buyer)
        self.client.post("/api/v1/messaging/blocks/", {"user": self.seller.pk}, format="json")
        r = self._start()
        self.assertEqual(r.status_code, 400, r.data)

    def test_clear_is_per_user_and_new_message_restores(self):
        r = self._start()
        self.assertEqual(r.status_code, 201, r.data)
        conversation_id = r.data["id"]

        self.client.force_authenticate(user=self.buyer)
        r = self.client.post(f"/api/v1/messaging/{conversation_id}/clear/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(self.client.get("/api/v1/messaging/").data["count"], 0)

        # Seller still sees the conversation.
        self.client.force_authenticate(user=self.seller)
        self.assertEqual(self.client.get("/api/v1/messaging/").data["count"], 1)

        # A new message restores it for both.
        Message.objects.create(
            conversation_id=conversation_id, sender=self.seller, body="Still there?"
        )
        self.client.force_authenticate(user=self.buyer)
        self.assertEqual(self.client.get("/api/v1/messaging/").data["count"], 1)

    def test_block_hides_existing_conversation(self):
        r = self._start()
        conversation_id = r.data["id"]
        self.client.force_authenticate(user=self.buyer)
        self.client.post("/api/v1/messaging/blocks/", {"user": self.seller.pk}, format="json")
        self.assertEqual(self.client.get("/api/v1/messaging/").data["count"], 0)
        self.assertEqual(
            self.client.get(f"/api/v1/messaging/{conversation_id}/messages/").status_code,
            404,
        )
