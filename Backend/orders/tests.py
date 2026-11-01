from decimal import Decimal
from itertools import count

from django.test import override_settings
from rest_framework.test import APITestCase

from accounts.models import User
from products.models import Product
from .models import Cart, CartItem, Order

_counter = count(1)

SHIPPING = {
    "recipient_name": "Ada Obi",
    "phone": "08012345678",
    "address": "12 Allen Avenue, Ikeja",
    "state": "lagos",
}


def make_user(prefix="user"):
    n = next(_counter)
    return User.objects.create_user(
        email=f"{prefix}{n}@example.com", username=f"{prefix}{n}", password="pass12345"
    )


def make_product(seller, **overrides):
    n = next(_counter)
    data = dict(
        product_user=seller,
        product_name=f"Test Item {n}",
        description="A nice product used only for testing purposes.",
        price=Decimal("5000.00"),
        category="fashion",
        sub_category="shoes",
        condition="new",
        color="red",
        quantity=5,
        state="lagos",
        city="ikeja",
        contact_methods=["phone_call"],
        contact_number="+2348012345678",
    )
    data.update(overrides)
    return Product.objects.create(**data)


class CartTests(APITestCase):
    def setUp(self):
        self.seller = make_user("seller")
        self.buyer = make_user("buyer")
        self.product = make_product(self.seller)
        self.client.force_authenticate(self.buyer)

    def add(self, product, quantity=1):
        return self.client.post(
            "/api/v1/orders/cart/items/",
            {"product_id": product.id, "quantity": quantity},
            format="json",
        )

    def test_add_to_cart_and_totals_use_backend_price(self):
        response = self.add(self.product, 2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("10000.00"))
        self.assertEqual(response.data["item_count"], 2)

    def test_client_cannot_inject_price(self):
        response = self.client.post(
            "/api/v1/orders/cart/items/",
            {"product_id": self.product.id, "quantity": 1, "price": "1.00"},
            format="json",
        )
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("5000.00"))

    def test_adding_same_product_accumulates(self):
        self.add(self.product, 1)
        response = self.add(self.product, 2)
        self.assertEqual(response.data["items"][0]["quantity"], 3)

    def test_cannot_exceed_stock(self):
        response = self.add(self.product, 6)
        self.assertEqual(response.status_code, 400)

    def test_invalid_quantities_rejected(self):
        for bad in (0, -1, "abc", 1000):
            self.assertEqual(self.add(self.product, bad).status_code, 400, bad)

    def test_cannot_buy_own_listing(self):
        self.client.force_authenticate(self.seller)
        self.assertEqual(self.add(self.product).status_code, 400)

    def test_non_purchasable_category_rejected(self):
        service = make_product(self.seller, category="services", sub_category="catering")
        self.assertEqual(self.add(service).status_code, 400)

    def test_update_quantity(self):
        self.add(self.product, 1)
        response = self.client.patch(
            f"/api/v1/orders/cart/items/{self.product.id}/", {"quantity": 4}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("20000.00"))

    def test_remove_item(self):
        self.add(self.product, 1)
        response = self.client.delete(f"/api/v1/orders/cart/items/{self.product.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["items"], [])

    def test_deleted_product_disappears_from_cart(self):
        self.add(self.product, 1)
        self.product.delete()
        response = self.client.get("/api/v1/orders/cart/")
        self.assertEqual(response.data["items"], [])

    def test_sold_out_item_flagged_unavailable_and_excluded_from_total(self):
        self.add(self.product, 1)
        Product.objects.filter(pk=self.product.pk).update(sold=True)
        response = self.client.get("/api/v1/orders/cart/")
        self.assertFalse(response.data["items"][0]["available"])
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("0"))

    def test_cart_requires_login(self):
        self.client.force_authenticate(None)
        self.assertIn(self.client.get("/api/v1/orders/cart/").status_code, (401, 403))


@override_settings(DELIVERY_FEE=1500)
class OrderTests(APITestCase):
    def setUp(self):
        self.seller = make_user("seller")
        self.buyer = make_user("buyer")
        self.other = make_user("other")
        self.p1 = make_product(self.seller, price=Decimal("5000.00"))
        self.p2 = make_product(self.seller, price=Decimal("2500.00"))
        self.client.force_authenticate(self.buyer)

    def fill_cart(self):
        cart = Cart.objects.create(user=self.buyer)
        CartItem.objects.create(cart=cart, product=self.p1, quantity=2)
        CartItem.objects.create(cart=cart, product=self.p2, quantity=1)

    def checkout(self, **extra):
        return self.client.post("/api/v1/orders/checkout/", {**SHIPPING, **extra}, format="json")

    def test_empty_cart_cannot_checkout(self):
        self.assertEqual(self.checkout().status_code, 400)

    def test_checkout_creates_order_with_correct_totals(self):
        self.fill_cart()
        response = self.checkout()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("12500.00"))
        self.assertEqual(Decimal(response.data["delivery_fee"]), Decimal("1500.00"))
        self.assertEqual(Decimal(response.data["total"]), Decimal("14000.00"))
        self.assertEqual(response.data["payment_status"], "unpaid")
        self.assertEqual(len(response.data["items"]), 2)
        self.assertTrue(response.data["reference"].startswith("NB-"))

    def test_checkout_ignores_client_supplied_totals(self):
        self.fill_cart()
        response = self.checkout(total="1.00", subtotal="1.00", payment_status="paid")
        self.assertEqual(Decimal(response.data["total"]), Decimal("14000.00"))
        self.assertEqual(response.data["payment_status"], "unpaid")

    def test_repeat_checkout_reuses_unpaid_order(self):
        self.fill_cart()
        first = self.checkout().data["reference"]
        second = self.checkout().data["reference"]
        self.assertEqual(first, second)
        self.assertEqual(Order.objects.filter(buyer=self.buyer).count(), 1)

    def test_changed_cart_cancels_previous_unpaid_order(self):
        self.fill_cart()
        first = self.checkout().data["reference"]
        CartItem.objects.filter(cart__user=self.buyer, product=self.p2).delete()
        second = self.checkout().data["reference"]
        self.assertNotEqual(first, second)
        self.assertEqual(Order.objects.get(reference=first).status, "cancelled")

    def test_price_snapshot_survives_price_change(self):
        self.fill_cart()
        reference = self.checkout().data["reference"]
        Product.objects.filter(pk=self.p1.pk).update(price=Decimal("99999.00"))
        detail = self.client.get(f"/api/v1/orders/{reference}/")
        self.assertEqual(Decimal(detail.data["total"]), Decimal("14000.00"))

    def test_checkout_blocked_when_item_unavailable(self):
        self.fill_cart()
        Product.objects.filter(pk=self.p1.pk).update(quantity=1)
        self.assertEqual(self.checkout().status_code, 400)

    def test_checkout_validates_shipping(self):
        self.fill_cart()
        response = self.client.post(
            "/api/v1/orders/checkout/", {**SHIPPING, "phone": "abc"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_other_user_cannot_see_or_cancel_order(self):
        self.fill_cart()
        reference = self.checkout().data["reference"]
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/v1/orders/{reference}/").status_code, 404)
        self.assertEqual(self.client.post(f"/api/v1/orders/{reference}/cancel/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/orders/").data["count"], 0)

    def test_buyer_can_cancel_unpaid_order(self):
        self.fill_cart()
        reference = self.checkout().data["reference"]
        response = self.client.post(f"/api/v1/orders/{reference}/cancel/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "cancelled")

    def test_sellers_do_not_see_unpaid_orders(self):
        self.fill_cart()
        self.checkout()
        self.client.force_authenticate(self.seller)
        self.assertEqual(self.client.get("/api/v1/orders/sales/").data["count"], 0)
