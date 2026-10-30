import base64
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from core.models import Category, City, State, SubCategory
from products.models import Product, ProductImage, ProductReport


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "YAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def make_product(owner, **overrides):
    data = {
        "product_user": owner,
        "product_name": "Apple iPhone 13",
        "description": "Clean used phone with box and charger included.",
        "price": Decimal("350000.00"),
        "category": "phones_tablets",
        "sub_category": "mobile_phones",
        "condition": "used",
        "color": "#111111",
        "quantity": 1,
        "negotiable": True,
        "state": "lagos",
        "city": "ikeja",
        "contact_methods": ["whatsapp"],
        "contact_number": "+2348012345678",
    }
    data.update(overrides)
    return Product.objects.create(**data)


class ProductAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Phones Tablets")
        cls.sub_category = SubCategory.objects.create(
            category=cls.category, name="Mobile Phones"
        )
        cls.state = State.objects.create(name="Lagos")
        cls.city = City.objects.create(state=cls.state, name="Ikeja")

        cls.seller = User.objects.create_user(
            email="seller@example.com",
            username="seller",
            password="StrongPass123!",
        )
        cls.buyer = User.objects.create_user(
            email="buyer@example.com",
            username="buyer",
            password="StrongPass123!",
        )


class ProductListTests(ProductAPITestCase):
    def test_list_is_public_and_paginated(self):
        make_product(self.seller)
        make_product(self.seller, product_name="Samsung Galaxy S22")

        response = self.client.get(reverse("products-list"), {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)

    def test_price_and_condition_filters(self):
        make_product(self.seller, price=Decimal("100000.00"))
        make_product(
            self.seller,
            product_name="Refurbished Pixel",
            price=Decimal("500000.00"),
            condition="refurbished",
        )

        response = self.client.get(
            reverse("products-list"),
            {
                "min_price": "200000",
                "max_price": "600000",
                "condition": "refurbished",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_name"], "Refurbished Pixel"
        )

    def test_location_and_delivery_filters(self):
        make_product(self.seller, state="lagos", city="ikeja")
        make_product(
            self.seller,
            product_name="Abuja Item",
            state="fct",
            city="abuja",
            delivery_available=True,
        )

        response = self.client.get(reverse("products-list"), {"state": "fct"})
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(
            reverse("products-list"), {"delivery_available": "true"}
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["product_name"], "Abuja Item")

    def test_sort_by_price_ascending(self):
        make_product(self.seller, price=Decimal("900000.00"))
        make_product(
            self.seller, product_name="Cheap Phone", price=Decimal("50000.00")
        )

        response = self.client.get(reverse("products-list"), {"sort": "price_asc"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"][0]["product_name"], "Cheap Phone"
        )

    def test_search_matches_name(self):
        make_product(self.seller, product_name="Apple iPhone 13")
        make_product(self.seller, product_name="Samsung Galaxy S22")

        response = self.client.get(reverse("products-list"), {"search": "iPhone"})

        self.assertEqual(response.data["count"], 1)

    def test_verified_seller_filter(self):
        other = User.objects.create_user(
            email="verified@example.com",
            username="verifieduser",
            password="StrongPass123!",
            verified=True,
        )
        make_product(self.seller)
        make_product(other, product_name="Verified Phone")

        response = self.client.get(
            reverse("products-list"), {"verified_seller": "true"}
        )

        self.assertEqual(response.data["count"], 1)


class ProductDetailTests(ProductAPITestCase):
    def test_detail_tracks_view_for_authenticated_non_owner(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.buyer)

        response = self.client.get(
            reverse("product-detail", kwargs={"product_slug": product.product_slug})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["views_count"], 1)
        self.assertTrue(product.views.filter(pk=self.buyer.pk).exists())
        self.assertEqual(response.data["product_user"]["verified"], False)

    def test_owner_can_mark_product_sold(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.seller)

        response = self.client.patch(
            reverse("product-detail", kwargs={"product_slug": product.product_slug}),
            {"sold": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertTrue(product.sold)
        self.assertFalse(product.active)
        self.assertEqual(product.listing_status, "sold")

    def test_non_owner_cannot_update_product(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.buyer)

        response = self.client.patch(
            reverse("product-detail", kwargs={"product_slug": product.product_slug}),
            {"price": "1000.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateProductTests(ProductAPITestCase):
    def test_create_product_sets_owner_and_expiry(self):
        self.client.force_authenticate(self.seller)

        payload = {
            "product_name": "Google Pixel 8",
            "description": "Brand new sealed Pixel 8 with warranty.",
            "price": "780000.00",
            "category": "phones_tablets",
            "sub_category": "mobile_phones",
            "condition": "new",
            "color": "#222222",
            "quantity": 1,
            "negotiable": False,
            "state": "lagos",
            "city": "ikeja",
            "contact_methods": ["phone_call", "whatsapp"],
            "contact_number": "08012345678",
            "delivery_available": True,
        }

        response = self.client.post(
            reverse("create-product"), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(product_slug=response.data["product_slug"])
        self.assertEqual(product.product_user, self.seller)
        self.assertIsNotNone(product.expires_at)
        self.assertTrue(product.delivery_available)
        self.assertEqual(product.listing_status, "active")

    def test_create_product_requires_authentication(self):
        response = self.client.post(reverse("create-product"), {}, format="json")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


class MyListingsTests(ProductAPITestCase):
    def test_my_listings_only_returns_own_products(self):
        make_product(self.seller)
        make_product(self.buyer, product_name="Buyer Phone")
        self.client.force_authenticate(self.seller)

        response = self.client.get(reverse("my-listings"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["product_user"]["id"], self.seller.id)

    def test_filter_my_listings_by_status(self):
        sold = make_product(self.seller, product_name="Sold Phone")
        sold.sold = True
        sold.active = False
        sold.save()
        make_product(self.seller, product_name="Live Phone")

        self.client.force_authenticate(self.seller)
        response = self.client.get(reverse("my-listings"), {"status": "sold"})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["listing_status"], "sold")

    def test_expired_listing_status(self):
        product = make_product(self.seller)
        product.expires_at = timezone.now() - timedelta(days=1)
        product.save(update_fields=["expires_at"])

        self.client.force_authenticate(self.seller)
        response = self.client.get(reverse("my-listings"), {"status": "expired"})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["listing_status"], "expired")


class FavoritesAndHistoryTests(ProductAPITestCase):
    def test_favorites_endpoint(self):
        product = make_product(self.seller)
        product.favorites.add(self.buyer)
        self.client.force_authenticate(self.buyer)

        response = self.client.get(reverse("favorite-products"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["is_favorited"])

    def test_toggle_favorite(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.buyer)
        url = reverse(
            "toggle-favorite-product",
            kwargs={"product_slug": product.product_slug},
        )

        response = self.client.post(url)
        self.assertTrue(response.data["favorited"])
        self.assertEqual(response.data["favorites_count"], 1)

        response = self.client.post(url)
        self.assertFalse(response.data["favorited"])
        self.assertEqual(response.data["favorites_count"], 0)

    def test_recently_viewed_endpoint(self):
        product = make_product(self.seller)
        product.views.add(self.buyer)
        self.client.force_authenticate(self.buyer)

        response = self.client.get(reverse("recently-viewed-products"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class ReportProductTests(ProductAPITestCase):
    def test_report_product(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.buyer)

        response = self.client.post(
            reverse("report-product", kwargs={"product_slug": product.product_slug}),
            {"reason": "scam", "details": "Asked for advance payment."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertTrue(
            ProductReport.objects.filter(
                product=product, reporter=self.buyer
            ).exists()
        )

    def test_cannot_report_same_product_twice(self):
        product = make_product(self.seller)
        ProductReport.objects.create(
            product=product, reporter=self.buyer, reason="scam"
        )
        self.client.force_authenticate(self.buyer)

        response = self.client.post(
            reverse("report-product", kwargs={"product_slug": product.product_slug}),
            {"reason": "scam"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_report_own_product(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.seller)

        response = self.client.post(
            reverse("report-product", kwargs={"product_slug": product.product_slug}),
            {"reason": "scam"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductImageTests(ProductAPITestCase):
    def _image(self):
        return SimpleUploadedFile("pixel.png", PNG_BYTES, content_type="image/png")

    def test_delete_own_image(self):
        product = make_product(self.seller)
        image = ProductImage.objects.create(product=product, image=self._image())
        self.client.force_authenticate(self.seller)

        response = self.client.post(
            reverse("delete-product-image", kwargs={"image_id": image.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ProductImage.objects.filter(pk=image.id).exists())

    def test_cannot_delete_another_users_image(self):
        product = make_product(self.seller)
        image = ProductImage.objects.create(product=product, image=self._image())
        self.client.force_authenticate(self.buyer)

        response = self.client.post(
            reverse("delete-product-image", kwargs={"image_id": image.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ProductImage.objects.filter(pk=image.id).exists())

    def test_replace_product_images(self):
        product = make_product(self.seller)
        ProductImage.objects.create(product=product, image=self._image())
        self.client.force_authenticate(self.seller)

        response = self.client.post(
            reverse("update-product-images", kwargs={"product_id": product.id}),
            {"images": [self._image()]},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductImage.objects.filter(product=product).count(), 1)
