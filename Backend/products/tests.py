import base64
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection

from accounts.models import User
from core.models import AttributeDefinition, AttributeOption, Category, City, State, SubCategory
from products.models import Product, ProductAttribute, ProductImage, ProductReport


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


class ProductAttributeAPITestCase(ProductAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.make = AttributeDefinition.objects.create(
            category=cls.category, name="Make", label="Make", data_type="select", required=True,
            filterable=True, sort_order=1,
        )
        AttributeOption.objects.create(definition=cls.make, value="apple", label="Apple")
        AttributeOption.objects.create(definition=cls.make, value="samsung", label="Samsung")
        cls.year = AttributeDefinition.objects.create(
            category=cls.category, sub_category=cls.sub_category, name="Year", label="Year",
            data_type="number", min_value=1990, max_value=2026, filterable=True, sort_order=2,
        )
        cls.storage = AttributeDefinition.objects.create(
            category=cls.category, name="Storage", label="Storage", data_type="select", sort_order=3,
        )
        for value in ("64gb", "128gb"):
            AttributeOption.objects.create(definition=cls.storage, value=value, label=value.upper())

    def _payload(self, **extra):
        payload = {
            "product_name": "Apple iPhone 13",
            "description": "Clean used phone with box and charger included.",
            "price": "350000.00",
            "category": "phones_tablets",
            "sub_category": "mobile_phones",
            "condition": "used",
            "color": "#111111",
            "quantity": 1,
            "state": "lagos",
            "city": "ikeja",
            "contact_methods": ["whatsapp"],
            "contact_number": "08012345678",
        }
        payload.update(extra)
        return payload


class AttributeDefinitionEndpointTests(ProductAttributeAPITestCase):
    def test_definitions_for_category(self):
        response = self.client.get(reverse("attribute-definitions"), {"category": "phones-tablets"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = {d["slug"] for d in response.data}
        self.assertEqual(slugs, {"make", "storage"})
        make = next(d for d in response.data if d["slug"] == "make")
        self.assertEqual(make["data_type"], "select")
        self.assertEqual({o["value"] for o in make["options"]}, {"apple", "samsung"})

    def test_definitions_include_subcategory_scope(self):
        response = self.client.get(
            reverse("attribute-definitions"),
            {"category": "phones-tablets", "sub_category": "mobile-phones"},
        )
        slugs = {d["slug"] for d in response.data}
        self.assertEqual(slugs, {"make", "storage", "year"})

    def test_definitions_unknown_category_returns_empty(self):
        response = self.client.get(reverse("attribute-definitions"), {"category": "nope"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class ProductAttributeWriteTests(ProductAttributeAPITestCase):
    def test_create_with_valid_attributes(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product"),
            self._payload(attributes={"make": "apple", "year": 2021, "storage": "128gb"}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(product_slug=response.data["product_slug"])
        self.assertEqual(ProductAttribute.objects.filter(product=product).count(), 3)
        year = ProductAttribute.objects.get(product=product, definition=self.year)
        self.assertEqual(year.value_number, Decimal("2021"))
        returned = {a["slug"]: a["value"] for a in response.data["attributes"]}
        self.assertEqual(returned["make"], "apple")
        self.assertEqual(returned["year"], 2021.0)

    def test_create_rejects_invalid_select_option(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product"), self._payload(attributes={"make": "blackberry"}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.count(), 0)

    def test_create_rejects_wrong_data_type(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product"), self._payload(attributes={"year": "not-a-number"}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.count(), 0)

    def test_create_rejects_missing_required_attribute(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product"), self._payload(attributes={"storage": "64gb"}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("make", response.data)

    def test_create_rejects_unknown_attribute(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product"), self._payload(attributes={"make": "apple", "bogus": 1}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("bogus", response.data)

    def test_create_without_attributes_keeps_legacy_compatibility(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(reverse("create-product"), self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(product_slug=response.data["product_slug"])
        self.assertEqual(ProductAttribute.objects.filter(product=product).count(), 0)
        self.assertEqual(response.data["attributes"], [])

    def test_update_attributes(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.seller)
        url = reverse("product-detail", kwargs={"product_slug": product.product_slug})

        response = self.client.patch(url, {"attributes": {"make": "samsung", "year": 2020}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductAttribute.objects.filter(product=product).count(), 2)

        # Re-submit a changed value; explicit null clears the attribute.
        response = self.client.patch(url, {"attributes": {"make": "apple", "year": None}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductAttribute.objects.filter(product=product).count(), 1)
        make = ProductAttribute.objects.get(product=product, definition=self.make)
        self.assertEqual(make.value_text, "apple")

    def test_update_without_attributes_leaves_values_untouched(self):
        product = make_product(self.seller)
        ProductAttribute.objects.create(
            product=product, definition=self.make, value_text="apple"
        )
        self.client.force_authenticate(self.seller)
        response = self.client.patch(
            reverse("product-detail", kwargs={"product_slug": product.product_slug}),
            {"negotiable": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductAttribute.objects.filter(product=product).count(), 1)


class ProductAttributeReadTests(ProductAttributeAPITestCase):
    def test_attributes_returned_on_detail_and_list(self):
        product = make_product(self.seller)
        ProductAttribute.objects.create(product=product, definition=self.year, value_number=Decimal("2019"))
        ProductAttribute.objects.create(product=product, definition=self.make, value_text="apple")

        detail = self.client.get(
            reverse("product-detail", kwargs={"product_slug": product.product_slug})
        )
        values = {a["slug"]: a["value"] for a in detail.data["attributes"]}
        self.assertEqual(values, {"make": "apple", "year": 2019.0})

        listing = self.client.get(reverse("products-list"))
        first = listing.data["results"][-1]
        self.assertEqual({a["slug"] for a in first["attributes"]}, {"make", "year"})


class ProductAttributeFilterTests(ProductAttributeAPITestCase):
    def _seed_products(self, price1="600000.00", price2="100000.00"):
        p1 = make_product(self.seller, product_name="iPhone 13", price=Decimal(price1))
        ProductAttribute.objects.create(product=p1, definition=self.make, value_text="apple")
        ProductAttribute.objects.create(product=p1, definition=self.year, value_number=Decimal("2021"))
        p2 = make_product(self.seller, product_name="Galaxy S22", price=Decimal(price2))
        ProductAttribute.objects.create(product=p2, definition=self.make, value_text="samsung")
        ProductAttribute.objects.create(product=p2, definition=self.year, value_number=Decimal("2022"))
        make_product(self.seller, product_name="Plain Listing")
        return p1, p2

    def test_exact_select_filter(self):
        self._seed_products()
        response = self.client.get(reverse("products-list"), {"attr_make": "apple"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["product_name"], "iPhone 13")

    def test_number_range_filter(self):
        self._seed_products()
        response = self.client.get(
            reverse("products-list"), {"attr_year_min": "2022", "attr_year_max": "2025"}
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["product_name"], "Galaxy S22")

    def test_unknown_attribute_param_is_ignored(self):
        self._seed_products()
        response = self.client.get(reverse("products-list"), {"attr_does_not_exist": "x"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_non_filterable_definition_is_ignored(self):
        self.storage.filterable = False
        self.storage.save(update_fields=["filterable"])
        self._seed_products()
        response = self.client.get(reverse("products-list"), {"attr_storage": "128gb"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_in_filter(self):
        self._seed_products()
        response = self.client.get(reverse("products-list"), {"attr_make__in": "apple,samsung"})
        self.assertEqual(response.data["count"], 2)

    def test_invalid_number_returns_400(self):
        self._seed_products()
        response = self.client.get(reverse("products-list"), {"attr_year_min": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_combines_with_category_filter(self):
        self._seed_products()
        response = self.client.get(
            reverse("products-list"),
            {"category": "phones-tablets", "attr_make": "samsung", "condition": "used"},
        )
        self.assertEqual(response.data["count"], 1)

    def test_sort_still_applies_after_attribute_filter(self):
        self._seed_products()
        response = self.client.get(
            reverse("products-list"), {"attr_make__in": "apple,samsung", "sort": "price_asc"}
        )
        names = [p["product_name"] for p in response.data["results"]]
        self.assertEqual(names, ["Galaxy S22", "iPhone 13"])


class ProductAttributeFacetTests(ProductAttributeAPITestCase):
    def test_facets_return_option_counts(self):
        p1 = make_product(self.seller, product_name="iPhone 13")
        ProductAttribute.objects.create(product=p1, definition=self.make, value_text="apple")
        p2 = make_product(self.seller, product_name="Galaxy S22")
        ProductAttribute.objects.create(product=p2, definition=self.make, value_text="samsung")
        make_product(self.seller, product_name="Plain Listing")

        response = self.client.get(
            reverse("products-list"), {"facets": "1", "category": "phones-tablets"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("facets", response.data)
        self.assertEqual(response.data["facets"]["make"]["apple"], 1)
        self.assertEqual(response.data["facets"]["make"]["samsung"], 1)

    def test_facets_absent_without_flag(self):
        make_product(self.seller)
        response = self.client.get(reverse("products-list"))
        self.assertNotIn("facets", response.data)

    def test_facets_respect_active_filters(self):
        p1 = make_product(self.seller, product_name="Expensive Phone", price=Decimal("900000.00"))
        ProductAttribute.objects.create(product=p1, definition=self.make, value_text="apple")
        p2 = make_product(self.seller, product_name="Cheap Phone", price=Decimal("50000.00"))
        ProductAttribute.objects.create(product=p2, definition=self.make, value_text="apple")

        response = self.client.get(
            reverse("products-list"),
            {"facets": "1", "category": "phones-tablets", "max_price": "600000"},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["facets"]["make"]["apple"], 1)

    def test_facets_exclude_own_attribute_filter(self):
        p1 = make_product(self.seller, product_name="iPhone 13")
        ProductAttribute.objects.create(product=p1, definition=self.make, value_text="apple")
        ProductAttribute.objects.create(product=p1, definition=self.year, value_number=Decimal("2021"))
        p2 = make_product(self.seller, product_name="Galaxy S22")
        ProductAttribute.objects.create(product=p2, definition=self.make, value_text="samsung")
        ProductAttribute.objects.create(product=p2, definition=self.year, value_number=Decimal("2022"))

        # Filtering by make=apple narrows the RESULT set to 1, but the make
        # facet itself must still report samsung (its own filter excluded).
        response = self.client.get(
            reverse("products-list"),
            {"facets": "1", "category": "phones-tablets", "attr_make": "apple"},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["facets"]["make"]["apple"], 1)
        self.assertEqual(response.data["facets"]["make"]["samsung"], 1)

    def test_multiselect_facets_and_filter(self):
        tags = AttributeDefinition.objects.create(
            category=self.category, name="Tags", label="Tags", data_type="multiselect",
            filterable=True, sort_order=9,
        )
        for value in ("new-arrival", "deal"):
            AttributeOption.objects.create(definition=tags, value=value, label=value)
        p1 = make_product(self.seller, product_name="Tagged Phone")
        ProductAttribute.objects.create(
            product=p1, definition=tags, value_list=["new-arrival", "deal"]
        )
        make_product(self.seller, product_name="Untagged Phone")

        response = self.client.get(
            reverse("products-list"),
            {"facets": "1", "category": "phones-tablets", "attr_tags__in": "deal"},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["facets"]["tags"]["new-arrival"], 1)
        self.assertEqual(response.data["facets"]["tags"]["deal"], 1)

class ListQueryCountTests(ProductAPITestCase):
    def test_product_list_uses_constant_queries(self):
        for i in range(10):
            product = make_product(self.seller, product_name=f"Phone {i}")
            product.favorites.add(self.buyer)
            product.views.add(self.buyer)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse("products-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 10)
        # Constant regardless of row count: base + count + prefetches + facets off.
        self.assertLessEqual(len(ctx.captured_queries), 25, f"{len(ctx.captured_queries)} queries: N+1 regressed")

    def test_create_image_by_direct_upload_key(self):
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage

        product = make_product(self.seller)
        key = f"naijabay/{self.seller.pk}/0123abcd.jpg"
        default_storage.save(key, ContentFile(PNG_BYTES))
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product-images"),
            {"product": product.id, "key": key},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image = ProductImage.objects.filter(product=product).first()
        self.assertEqual(image.image.name, key)
        image.delete()
        default_storage.delete(key)

    def test_create_image_rejects_missing_direct_key(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product-images"),
            {"product": product.id, "key": f"naijabay/{self.seller.pk}/never-uploaded.jpg"},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_image_upload_rejected_by_content_sniff(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.seller)
        disguised = SimpleUploadedFile("photo.png", b"this is not an image", content_type="image/png")
        response = self.client.post(
            reverse("create-product-images"),
            {"product": product.id, "images": [disguised]},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_image_rejects_foreign_key(self):
        product = make_product(self.seller)
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-product-images"),
            {"product": product.id, "key": "naijabay/999999/other.jpg"},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
