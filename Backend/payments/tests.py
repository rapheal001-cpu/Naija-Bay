import hashlib
import hmac
import json
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from orders.models import Cart, CartItem, Order
from orders.tests import SHIPPING, make_product, make_user
from products.models import Product
from . import paystack
from .models import BoostPlan, ListingBoost, Payment, WebhookEvent
from .services import expire_boosts

KEY = "sk_test_dummy_key_for_tests"


def gateway_success(payment, **overrides):
    data = {
        "status": "success",
        "reference": payment.reference,
        "amount": int(payment.amount * 100),
        "currency": "NGN",
        "id": 4242,
        "gateway_response": "Successful",
    }
    data.update(overrides)
    return data


def sign(body):
    return hmac.new(KEY.encode(), body, hashlib.sha512).hexdigest()


@override_settings(PAYSTACK_SECRET_KEY=KEY, DELIVERY_FEE=1000, FRONTEND_URL="http://localhost:5173")
class OrderPaymentTests(APITestCase):
    def setUp(self):
        self.seller = make_user("seller")
        self.buyer = make_user("buyer")
        self.product = make_product(self.seller, price=Decimal("5000.00"), quantity=3)
        cart = Cart.objects.create(user=self.buyer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.client.force_authenticate(self.buyer)
        self.order_ref = self.client.post(
            "/api/v1/orders/checkout/", SHIPPING, format="json"
        ).data["reference"]

    def initialize(self):
        with mock.patch(
            "payments.paystack.initialize_transaction",
            return_value={"authorization_url": "https://checkout.paystack.com/abc"},
        ) as fake:
            response = self.client.post(f"/api/v1/payments/orders/{self.order_ref}/initialize/")
        return response, fake

    def verify(self, payment, **overrides):
        with mock.patch(
            "payments.paystack.verify_transaction",
            return_value=gateway_success(payment, **overrides),
        ):
            return self.client.get(f"/api/v1/payments/verify/{payment.reference}/")

    def test_initialize_uses_backend_total_in_kobo(self):
        response, fake = self.initialize()
        self.assertEqual(response.status_code, 201)
        self.assertIn("authorization_url", response.data)
        kwargs = fake.call_args.kwargs
        self.assertEqual(kwargs["amount_kobo"], 1100000)  # (2 x 5000 + 1000) x 100
        self.assertEqual(kwargs["email"], self.buyer.email)
        payment = Payment.objects.get(reference=response.data["reference"])
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.amount, Decimal("11000.00"))

    def test_other_user_cannot_pay_for_my_order(self):
        self.client.force_authenticate(make_user("other"))
        self.assertEqual(
            self.client.post(f"/api/v1/payments/orders/{self.order_ref}/initialize/").status_code, 404
        )

    def test_successful_verification_marks_order_paid_and_updates_stock(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        response = self.verify(payment)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        order = Order.objects.get(reference=self.order_ref)
        self.assertEqual(order.payment_status, "paid")
        self.assertIsNotNone(order.paid_at)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 1)
        self.assertEqual(self.product.sold_count, 2)
        self.assertFalse(CartItem.objects.filter(cart__user=self.buyer).exists())

    def test_verification_is_idempotent(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        self.verify(payment)
        self.verify(payment)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 1)  # decremented once only
        self.assertEqual(self.product.sold_count, 2)

    def test_amount_mismatch_is_rejected(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        response = self.verify(payment, amount=100)
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(Order.objects.get(reference=self.order_ref).payment_status, "unpaid")

    def test_currency_mismatch_is_rejected(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        response = self.verify(payment, currency="USD")
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(Order.objects.get(reference=self.order_ref).payment_status, "unpaid")

    def test_failed_payment_leaves_order_unpaid_and_payable_again(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        response = self.verify(payment, status="failed", gateway_response="Declined")
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(Order.objects.get(reference=self.order_ref).payment_status, "unpaid")
        self.assertEqual(self.initialize()[0].status_code, 201)  # can retry

    def test_abandoned_and_pending_states(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        self.assertEqual(self.verify(payment, status="ongoing").data["status"], "pending")
        self.assertEqual(self.verify(payment, status="abandoned").data["status"], "abandoned")
        self.assertEqual(Order.objects.get(reference=self.order_ref).payment_status, "unpaid")

    def test_unknown_transaction_stays_pending(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        with mock.patch(
            "payments.paystack.verify_transaction", side_effect=paystack.PaystackNotFound("nope")
        ):
            response = self.client.get(f"/api/v1/payments/verify/{payment.reference}/")
        self.assertEqual(response.data["status"], "pending")

    def test_gateway_outage_does_not_mark_paid(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        with mock.patch(
            "payments.paystack.verify_transaction", side_effect=paystack.PaystackError("down")
        ):
            response = self.client.get(f"/api/v1/payments/verify/{payment.reference}/")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(Order.objects.get(reference=self.order_ref).payment_status, "unpaid")

    def test_cannot_verify_someone_elses_payment(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        self.client.force_authenticate(make_user("other"))
        self.assertEqual(self.client.get(f"/api/v1/payments/verify/{payment.reference}/").status_code, 404)

    def test_cannot_pay_twice(self):
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        self.verify(payment)
        self.assertEqual(self.initialize()[0].status_code, 400)

    def test_seller_manages_fulfilment_only_after_payment(self):
        item = Order.objects.get(reference=self.order_ref).items.first()
        self.client.force_authenticate(self.seller)
        self.assertEqual(
            self.client.post(f"/api/v1/orders/sales/{item.id}/status/", {"status": "processing"}, format="json").status_code,
            400,
        )
        self.client.force_authenticate(self.buyer)
        payment = Payment.objects.get(reference=self.initialize()[0].data["reference"])
        self.verify(payment)

        self.client.force_authenticate(self.seller)
        self.assertEqual(self.client.get("/api/v1/orders/sales/").data["count"], 1)
        ok = self.client.post(f"/api/v1/orders/sales/{item.id}/status/", {"status": "processing"}, format="json")
        self.assertEqual(ok.status_code, 200)
        skip = self.client.post(f"/api/v1/orders/sales/{item.id}/status/", {"status": "delivered"}, format="json")
        self.assertEqual(skip.status_code, 400)  # cannot skip steps
        # a stranger cannot touch it
        self.client.force_authenticate(make_user("stranger"))
        self.assertEqual(
            self.client.post(f"/api/v1/orders/sales/{item.id}/status/", {"status": "shipped"}, format="json").status_code,
            404,
        )


@override_settings(PAYSTACK_SECRET_KEY=KEY)
class WebhookTests(APITestCase):
    def setUp(self):
        self.seller = make_user("seller")
        self.buyer = make_user("buyer")
        self.product = make_product(self.seller, quantity=4)
        cart = Cart.objects.create(user=self.buyer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        self.client.force_authenticate(self.buyer)
        ref = self.client.post("/api/v1/orders/checkout/", SHIPPING, format="json").data["reference"]
        self.order = Order.objects.get(reference=ref)
        self.payment = Payment.objects.create(
            reference="NBO-WEBHOOKTEST", user=self.buyer, purpose="order",
            order=self.order, amount=self.order.total,
        )
        self.client.force_authenticate(None)

    def post_webhook(self, body, signature=None):
        raw = json.dumps(body).encode()
        return self.client.post(
            "/api/v1/payments/webhook/", data=raw, content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature if signature is not None else sign(raw),
        )

    def body(self):
        return {"event": "charge.success", "data": {"id": 99, "reference": self.payment.reference}}

    def test_invalid_signature_rejected(self):
        with mock.patch("payments.paystack.verify_transaction") as verify:
            response = self.post_webhook(self.body(), signature="bad")
        self.assertEqual(response.status_code, 401)
        verify.assert_not_called()
        self.assertEqual(Order.objects.get(pk=self.order.pk).payment_status, "unpaid")

    def test_missing_signature_rejected(self):
        response = self.client.post(
            "/api/v1/payments/webhook/", data=b"{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_webhook_marks_paid_after_reverification(self):
        with mock.patch("payments.paystack.verify_transaction", return_value=gateway_success(self.payment)):
            response = self.post_webhook(self.body())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.get(pk=self.order.pk).payment_status, "paid")

    def test_webhook_body_alone_is_not_trusted(self):
        # Paystack says the charge was NOT successful -> body claiming success is ignored.
        with mock.patch(
            "payments.paystack.verify_transaction",
            return_value=gateway_success(self.payment, status="failed"),
        ):
            self.post_webhook(self.body())
        self.assertEqual(Order.objects.get(pk=self.order.pk).payment_status, "unpaid")

    def test_duplicate_webhook_processed_once(self):
        with mock.patch("payments.paystack.verify_transaction", return_value=gateway_success(self.payment)) as verify:
            self.post_webhook(self.body())
            self.post_webhook(self.body())
        self.assertEqual(verify.call_count, 1)
        self.assertEqual(WebhookEvent.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)

    def test_webhook_then_callback_does_not_double_fulfil(self):
        with mock.patch("payments.paystack.verify_transaction", return_value=gateway_success(self.payment)):
            self.post_webhook(self.body())
            self.client.force_authenticate(self.buyer)
            self.client.get(f"/api/v1/payments/verify/{self.payment.reference}/")
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)

    def test_unknown_reference_acknowledged_without_error(self):
        body = {"event": "charge.success", "data": {"id": 1, "reference": "NOT-OURS"}}
        self.assertEqual(self.post_webhook(body).status_code, 200)

    def test_gateway_error_returns_500_so_paystack_retries(self):
        with mock.patch("payments.paystack.verify_transaction", side_effect=paystack.PaystackError("down")):
            response = self.post_webhook(self.body())
        self.assertEqual(response.status_code, 500)
        self.assertEqual(WebhookEvent.objects.count(), 0)  # rolled back => retry will run


@override_settings(PAYSTACK_SECRET_KEY=KEY)
class BoostTests(APITestCase):
    def setUp(self):
        self.seller = make_user("seller")
        self.other = make_user("other")
        self.product = make_product(self.seller)
        self.plan = BoostPlan.objects.create(
            name="Basic", slug="basic", price=Decimal("1500.00"), duration_days=3, boost_level=1
        )
        self.client.force_authenticate(self.seller)

    def start(self, product=None, plan=None):
        with mock.patch(
            "payments.paystack.initialize_transaction",
            return_value={"authorization_url": "https://checkout.paystack.com/x"},
        ) as fake:
            response = self.client.post(
                "/api/v1/payments/boost/initialize/",
                {"product_id": (product or self.product).id, "plan_id": (plan or self.plan).id},
                format="json",
            )
        return response, fake

    def verify(self, reference, **overrides):
        payment = Payment.objects.get(reference=reference)
        with mock.patch("payments.paystack.verify_transaction", return_value=gateway_success(payment, **overrides)):
            return self.client.get(f"/api/v1/payments/verify/{reference}/")

    def test_plans_are_listed_with_price_and_duration(self):
        BoostPlan.objects.create(name="Hidden", slug="hidden", price=Decimal("500"), duration_days=1, is_active=False)
        self.client.force_authenticate(None)
        response = self.client.get("/api/v1/payments/boost/plans/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p["slug"] for p in response.data], ["basic"])
        self.assertEqual(response.data[0]["duration_days"], 3)

    def test_initialize_charges_plan_price(self):
        response, fake = self.start()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(fake.call_args.kwargs["amount_kobo"], 150000)

    def test_cannot_boost_someone_elses_listing(self):
        self.client.force_authenticate(self.other)
        response, _ = self.start()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Payment.objects.count(), 0)

    def test_inactive_plan_rejected(self):
        self.plan.is_active = False
        self.plan.save()
        self.assertEqual(self.start()[0].status_code, 400)

    def test_unpaid_boost_never_activates(self):
        reference = self.start()[0].data["reference"]
        self.product.refresh_from_db()
        self.assertFalse(self.product.promoted)
        self.verify(reference, status="failed")
        self.product.refresh_from_db()
        self.assertFalse(self.product.promoted)
        self.assertEqual(ListingBoost.objects.get().status, "failed")

    def test_wrong_amount_never_activates(self):
        reference = self.start()[0].data["reference"]
        self.verify(reference, amount=1)
        self.product.refresh_from_db()
        self.assertFalse(self.product.promoted)

    def test_verified_payment_activates_boost_once(self):
        reference = self.start()[0].data["reference"]
        response = self.verify(reference)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["boost"]["effective_status"], "active")
        self.product.refresh_from_db()
        self.assertTrue(self.product.promoted)
        self.assertEqual(self.product.boost_level, 1)
        first_expiry = self.product.promoted_until
        self.assertAlmostEqual(
            (first_expiry - timezone.now()).total_seconds(), 3 * 86400, delta=60
        )
        self.verify(reference)  # replay must not extend the boost
        self.product.refresh_from_db()
        self.assertEqual(self.product.promoted_until, first_expiry)
        self.assertEqual(ListingBoost.objects.count(), 1)

    def test_cannot_start_second_boost_while_active(self):
        self.verify(self.start()[0].data["reference"])
        self.assertEqual(self.start()[0].status_code, 400)

    def test_boosted_listings_rank_first(self):
        newer = make_product(self.seller, product_name="Newer Unboosted Item")
        self.verify(self.start()[0].data["reference"])
        self.client.force_authenticate(None)
        results = self.client.get("/api/v1/products/").data["results"]
        self.assertEqual(results[0]["id"], self.product.id)
        self.assertTrue(results[0]["is_boosted"])
        self.assertIn(newer.id, [r["id"] for r in results])

    def test_expiry_switches_boost_off(self):
        self.verify(self.start()[0].data["reference"])
        past = timezone.now() - timedelta(minutes=1)
        ListingBoost.objects.update(expires_at=past)
        Product.objects.filter(pk=self.product.pk).update(promoted_until=past)
        self.assertEqual(expire_boosts(), 1)
        self.product.refresh_from_db()
        self.assertFalse(self.product.promoted)
        self.assertEqual(self.product.boost_level, 0)
        self.assertEqual(ListingBoost.objects.get().status, "expired")
        self.assertEqual(expire_boosts(), 0)  # idempotent
        # and the seller can boost again afterwards
        self.assertEqual(self.start()[0].status_code, 201)

    def test_my_boosts_lists_active_and_expired(self):
        self.verify(self.start()[0].data["reference"])
        response = self.client.get("/api/v1/payments/boost/my/?status=active")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(self.client.get("/api/v1/payments/boost/my/?status=expired").data["count"], 0)
