from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Follow, Notifications, Store, User


class StoreAPITests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="seller@example.com",
            username="seller",
            password="StrongPass123!",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="StrongPass123!",
        )

    def test_create_store_generates_unique_slug(self):
        self.client.force_authenticate(self.seller)
        response = self.client.post(
            reverse("create-store"),
            {"name": "Kiddo Connect", "description": "Gadgets store"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["slug"], "kiddo-connect")
        self.assertTrue(Store.objects.filter(user=self.seller).exists())

    def test_create_store_twice_updates_existing_store(self):
        self.client.force_authenticate(self.seller)
        self.client.post(
            reverse("create-store"), {"name": "First Store"}, format="json"
        )
        response = self.client.post(
            reverse("create-store"), {"name": "Renamed Store"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Store.objects.filter(user=self.seller).count(), 1)
        store = Store.objects.get(user=self.seller)
        self.assertEqual(store.name, "Renamed Store")
        self.assertEqual(store.slug, "renamed-store")

    def test_store_detail_is_public(self):
        store = Store.objects.create(user=self.seller, name="Public Store")

        response = self.client.get(
            reverse("store-detail", kwargs={"slug": store.slug})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Public Store")
        self.assertEqual(response.data["owner"]["username"], "seller")

    def test_only_owner_can_update_store(self):
        store = Store.objects.create(user=self.seller, name="Mine")
        self.client.force_authenticate(self.other)

        response = self.client.patch(
            reverse("store-detail", kwargs={"slug": store.slug}),
            {"description": "Hijacked"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        store.refresh_from_db()
        self.assertEqual(store.description, "")

    def test_only_owner_can_delete_store(self):
        store = Store.objects.create(user=self.seller, name="Mine")
        self.client.force_authenticate(self.other)

        response = self.client.delete(
            reverse("store-detail", kwargs={"slug": store.slug})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Store.objects.filter(pk=store.pk).exists())

    def test_duplicate_store_name_is_rejected(self):
        Store.objects.create(user=self.seller, name="Taken Name")
        self.client.force_authenticate(self.other)

        response = self.client.post(
            reverse("create-store"), {"name": "Taken Name"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_my_store_returns_404_before_creation(self):
        self.client.force_authenticate(self.seller)
        response = self.client.get(reverse("my-store"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FollowAPITests(APITestCase):
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

    def test_toggle_follow_creates_and_removes_follow(self):
        self.client.force_authenticate(self.buyer)
        url = reverse("toggle-follow-user", kwargs={"user_id": self.seller.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["following"])
        self.assertEqual(response.data["followers_count"], 1)
        self.assertTrue(
            Follow.objects.filter(
                follower=self.buyer, following=self.seller
            ).exists()
        )
        self.assertTrue(
            Notifications.objects.filter(
                user=self.seller, notification_type="new_follower"
            ).exists()
        )

        response = self.client.post(url)
        self.assertFalse(response.data["following"])
        self.assertEqual(response.data["followers_count"], 0)
        self.assertFalse(
            Follow.objects.filter(
                follower=self.buyer, following=self.seller
            ).exists()
        )

    def test_cannot_follow_self(self):
        self.client.force_authenticate(self.buyer)
        response = self.client.post(
            reverse("toggle-follow-user", kwargs={"user_id": self.buyer.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_requires_authentication(self):
        response = self.client.post(
            reverse("toggle-follow-user", kwargs={"user_id": self.seller.id})
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_followers_and_following_lists(self):
        Follow.objects.create(follower=self.buyer, following=self.seller)

        response = self.client.get(
            reverse("followers-list", kwargs={"pk": self.seller.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], "buyer")

        response = self.client.get(
            reverse("following-list", kwargs={"pk": self.buyer.id})
        )
        results = response.data.get("results", response.data)
        self.assertEqual(results[0]["username"], "seller")
