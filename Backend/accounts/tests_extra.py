"""End-to-end tests for the Jiji-style features added in 2026-11."""

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Product


class JijiFeaturesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seller = User.objects.create_user(
            email="seller@test.local", username="jijiseller", password="TestPass123!"
        )
        cls.buyer = User.objects.create_user(
            email="buyer@test.local", username="jijibuyer", password="TestPass123!"
        )
        cls.product = Product.objects.create(
            product_user=cls.seller,
            product_name="Jiji feature test item",
            description="Test description",
            price=Decimal("10000.00"),
            category="phones_tablets",
            sub_category="mobile_phones",
            condition="used",
            color="Black",
            quantity=1,
            state="lagos",
            city="ikeja",
            contact_methods=["whatsapp"],
            contact_number="+2348012345678",
        )

    def setUp(self):
        self.client = APIClient()

    def test_feedback_create_and_list(self):
        self.client.force_authenticate(user=self.buyer)
        r = self.client.post(
            "/api/v1/accounts/auth/feedback/create/",
            {"seller": self.seller.id, "rating": 5, "comment": "Great seller"},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.get(f"/api/v1/accounts/auth/feedback/?seller={self.seller.id}")
        self.assertEqual(r.status_code, 200, r.data)

    def test_saved_search(self):
        self.client.force_authenticate(user=self.buyer)
        r = self.client.post(
            "/api/v1/accounts/auth/saved-searches/",
            {"name": "iphones", "query_params": {"search": "iphone"}},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.get("/api/v1/accounts/auth/saved-searches/")
        self.assertEqual(r.status_code, 200, r.data)

    def test_verification_status(self):
        self.client.force_authenticate(user=self.buyer)
        r = self.client.get("/api/v1/accounts/auth/verification/me/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["status"], "none")

    def test_offers_callbacks_videos(self):
        self.client.force_authenticate(user=self.buyer)
        slug = self.product.product_slug
        r = self.client.post(
            f"/api/v1/products/{slug}/offers/",
            {"amount": "9000.00", "message": "Can you do 9k?"},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.post(
            f"/api/v1/products/{slug}/callbacks/",
            {"phone": "+2348012345678"},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.get(f"/api/v1/products/{slug}/videos/")
        self.assertEqual(r.status_code, 200, r.data)

        self.client.force_authenticate(user=self.seller)
        r = self.client.get(f"/api/v1/products/{slug}/offers/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(len(r.data["results"]), 1)

    def test_monetisation_endpoints(self):
        self.client.force_authenticate(user=self.buyer)
        for path in (
            "/api/v1/payments/credit/",
            "/api/v1/payments/credit/transactions/",
            "/api/v1/payments/referrals/",
            "/api/v1/payments/boost/auto-renew/",
            "/api/v1/payments/pro-sales/",
        ):
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(
            "/api/v1/payments/pro-sales/",
            {
                "product": self.product.id,
                "name": "Test campaign",
                "daily_budget": "1000.00",
                "bid_amount": "20.00",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)

    def test_safe_deal_lifecycle(self):
        order = Order.objects.create(
            reference="NB-SMKTEST01",
            buyer=self.buyer,
            seller=self.seller,
            is_safe_deal=True,
            escrow_status="paid",
            payment_status="paid",
            subtotal=Decimal("10000.00"),
            delivery_fee=Decimal("0.00"),
            total=Decimal("10000.00"),
            recipient_name="Test Buyer",
            phone="+2348012345678",
            address="Lagos",
            state="lagos",
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            seller=self.seller,
            product_name=self.product.product_name,
            unit_price=self.product.price,
            quantity=1,
            line_total=self.product.price,
        )
        base = f"/api/v1/orders/{order.reference}/safe-deal/"

        self.client.force_authenticate(user=self.seller)
        r = self.client.post(base + "accept/", {"delivery_service": "Courier"}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["escrow_status"], "shipped")

        r = self.client.post(base + "tracking/", {"tracking_number": "TRK123"}, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(base + "delivered/", {}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["escrow_status"], "delivered")
        self.assertIsNotNone(r.data["confirm_deadline"])

        self.client.force_authenticate(user=self.buyer)
        r = self.client.post(base + "confirm/", {}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["escrow_status"], "confirmed")
        self.assertIsNotNone(r.data["seller_payout_at"])

        r = self.client.get("/api/v1/orders/safe-deal/")
        self.assertEqual(r.status_code, 200, r.data)

    def test_safe_deal_problem_holds_funds(self):
        order = Order.objects.create(
            reference="NB-SMKTEST02",
            buyer=self.buyer,
            seller=self.seller,
            is_safe_deal=True,
            escrow_status="delivered",
            payment_status="paid",
            subtotal=Decimal("10000.00"),
            delivery_fee=Decimal("0.00"),
            total=Decimal("10000.00"),
            recipient_name="Test Buyer",
            phone="+2348012345678",
            address="Lagos",
            state="lagos",
        )
        self.client.force_authenticate(user=self.buyer)
        r = self.client.post(
            f"/api/v1/orders/{order.reference}/safe-deal/problem/",
            {"reason": "Item damaged"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["escrow_status"], "disputed")
        order.refresh_from_db()
        self.assertIsNone(order.seller_payout_at)
