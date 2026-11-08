"""One-command seeding for every Naija-Bay model.

Usage::

    python manage.py seed_all                 # idempotent, no images
    python manage.py seed_all --images        # also generate placeholder photos
    python manage.py seed_all --clear         # wipe seeded data first
    python manage.py seed_all --users 10 --products-per-user 15
"""

import random
from datetime import timedelta
from decimal import Decimal

from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Follow, Notifications, Store, User
from NaijaBay.management.commands.categories import seed_categories
from NaijaBay.management.commands.nigeria_states import seed_locations
from NaijaBay.management.commands.seed_products import (
    COLORS,
    PRODUCT_CATALOG,
    attach_images_to_product,
    generate_description,
    get_price,
)
from core.models import Category, City, State, SubCategory
from messaging.models import Conversation, Message
from NaijaBay.utils import (
    CONDITION_CHOICES,
    CONTACT_METHOD_CHOICES,
    STATE_CITY_MAP,
    _city_slug,
)
from products.models import Product, ProductRating, ProductReport


SELLER_NAMES = [
    ("Kiddo", "Connect"),
    ("Mega", "Gadgets"),
    ("Prime", "Autos"),
    ("Naija", "Homes"),
    ("Trendy", "Fashion"),
    ("Power", "Tools"),
    ("Green", "Farm"),
    ("Smart", "Tech"),
    ("Royal", "Furniture"),
    ("Fast", "Deals"),
]

BUYER_NAMES = [
    ("Ada", "Okafor"),
    ("Chinedu", "Eze"),
    ("Aisha", "Bello"),
    ("Tunde", "Adeyemi"),
    ("Ngozi", "Nwosu"),
    ("Ibrahim", "Musa"),
    ("Funke", "Adebayo"),
    ("Emeka", "Obi"),
    ("Zainab", "Yusuf"),
    ("Samuel", "Johnson"),
]

MESSAGE_TEMPLATES = [
    "Hello, is this still available?",
    "Yes, it is still available.",
    "What is your last price?",
    "The price is slightly negotiable. What is your offer?",
    "Can we meet around Ikeja tomorrow?",
    "That works for me. Let us agree on a time.",
    "Does it come with a warranty?",
    "Yes, there is a short warranty on this item.",
    "Please send more pictures.",
    "I will upload more pictures shortly.",
]


class Command(BaseCommand):
    help = "Seed every Naija-Bay model with realistic, idempotent sample data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete seeded marketplace data before seeding (superusers are kept).",
        )
        parser.add_argument(
            "--images",
            action="store_true",
            help="Generate 6-10 placeholder images per product (slower).",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=8,
            help="Number of seller accounts to create (default: 8).",
        )
        parser.add_argument(
            "--products-per-user",
            type=int,
            default=12,
            help="Products per seller (default: 12).",
        )
        parser.add_argument(
            "--conversations",
            type=int,
            default=6,
            help="Number of buyer/seller conversations to create (default: 6).",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="TestPass123!",
            help="Password assigned to every seeded account.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for reproducible fixtures (default: 42).",
        )

    # -------------------------------------------------------------------------
    # Entry point
    # -------------------------------------------------------------------------

    def handle(self, *args, **options):
        self.rng = random.Random(options["seed"])
        self.password = options["password"]
        self.with_images = options["images"]

        if options["clear"]:
            self._clear()

        with transaction.atomic():
            states, cities = self._seed_locations()
            categories, subcategories = self._seed_categories()
            sellers, buyers = self._seed_users(options["users"])
            stores = self._seed_stores(sellers)
            self._seed_follows(sellers, buyers)
            products = self._seed_products(
                sellers, categories, subcategories, cities, options["products_per_user"]
            )

            # Social data covers EVERY product and user in the database (not
            # just the ones created above), so listings made by create_user /
            # seed_products also get favorites, views, ratings and chats.
            all_products = list(Product.objects.order_by("id"))
            all_users = list(User.objects.filter(is_active=True).order_by("id"))

            self._seed_engagement(all_products, [], all_users)
            self._seed_ratings(all_products, all_users, [])
            self._seed_conversations(
                all_products, [], all_users, options["conversations"]
            )
            self._seed_reports(all_products, all_users)
            self._seed_notifications(all_users)

        self._summary()

    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def _clear(self):
        self.stdout.write(self.style.WARNING("Clearing marketplace data..."))

        ProductRating.objects.all().delete()
        ProductReport.objects.all().delete()
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Notifications.objects.all().delete()
        Follow.objects.all().delete()
        Store.objects.all().delete()
        Product.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        SubCategory.objects.all().delete()
        Category.objects.all().delete()
        City.objects.all().delete()
        State.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Marketplace data cleared."))

    # -------------------------------------------------------------------------
    # Locations
    # -------------------------------------------------------------------------

    def _seed_locations(self):
        # Shared with the ``nigeria_states`` command so both stay identical.
        return seed_locations(self)

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    def _seed_categories(self):
        # Shared with the ``categories`` command so both stay identical.
        return seed_categories(self)

    # -------------------------------------------------------------------------
    # Users & stores
    # -------------------------------------------------------------------------

    def _seed_users(self, seller_count):
        sellers = []
        buyers = []

        for index in range(max(seller_count, 1)):
            first, last = SELLER_NAMES[index % len(SELLER_NAMES)]
            username = f"seedseller{index + 1}"
            user, _ = User.objects.get_or_create(
                email=f"{username}@naijabay.test",
                defaults={
                    "username": username,
                    "first_name": first,
                    "last_name": last,
                    "state": self.rng.choice(
                        [s for s in STATE_CITY_MAP if s]
                    ),
                    "verified": index < max(2, seller_count // 3),
                    "is_active": True,
                },
            )
            user.set_password(self.password)
            user.save(update_fields=["password"])
            sellers.append(user)

        buyer_total = max(3, seller_count)
        for index in range(buyer_total):
            first, last = BUYER_NAMES[index % len(BUYER_NAMES)]
            username = f"seedbuyer{index + 1}"
            user, _ = User.objects.get_or_create(
                email=f"{username}@naijabay.test",
                defaults={
                    "username": username,
                    "first_name": first,
                    "last_name": last,
                    "state": self.rng.choice(
                        [s for s in STATE_CITY_MAP if s]
                    ),
                    "is_active": True,
                },
            )
            user.set_password(self.password)
            user.save(update_fields=["password"])
            buyers.append(user)

        # allauth requires a verified primary email before login
        for user in sellers + buyers:
            EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": True, "primary": True},
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Users: {len(sellers)} sellers, {len(buyers)} buyers "
                f"(password: {self.password})."
            )
        )
        return sellers, buyers

    def _seed_stores(self, sellers):
        stores = []
        for index, seller in enumerate(sellers):
            first, last = SELLER_NAMES[index % len(SELLER_NAMES)]
            store_name = f"{first} {last} Store"
            if index >= len(SELLER_NAMES):
                store_name = f"{store_name} {index + 1}"

            store, _ = Store.objects.get_or_create(
                user=seller,
                defaults={
                    "name": store_name,
                    "description": (
                        f"{first} {last} is a trusted Naija-Bay seller offering "
                        "quality products with fast replies and safe delivery."
                    ),
                    "verified": seller.verified,
                    "state": seller.state,
                    "address": f"{index + 1} Market Road, Nigeria",
                },
            )
            stores.append(store)

        self.stdout.write(self.style.SUCCESS(f"Stores: {len(stores)} stores."))
        return stores

    def _seed_follows(self, sellers, buyers):
        created = 0
        for buyer in buyers:
            for seller in self.rng.sample(sellers, k=min(2, len(sellers))):
                _, was_created = Follow.objects.get_or_create(
                    follower=buyer, following=seller
                )
                created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"Follows: {created} new follows."))

    # -------------------------------------------------------------------------
    # Products
    # -------------------------------------------------------------------------

    def _seed_products(self, sellers, categories, subcategories, cities, per_user):
        conditions = [c[0] for c in CONDITION_CHOICES if c[0]]
        contact_methods_all = [m[0] for m in CONTACT_METHOD_CHOICES if m[0]]
        states_list = list(State.objects.all())
        valid_categories = [
            key for key in PRODUCT_CATALOG if key in categories
        ]

        products = []
        created = 0

        for seller in sellers:
            for index in range(per_user):
                category = self.rng.choice(valid_categories)
                sub_category = self.rng.choice(
                    list(PRODUCT_CATALOG[category].keys())
                )
                name = self.rng.choice(PRODUCT_CATALOG[category][sub_category])

                state_slug = self.rng.choice(list(cities.keys()))
                city_objects = cities.get(state_slug) or []
                if city_objects:
                    city_slug = _city_slug(self.rng.choice(city_objects).name)
                else:
                    city_slug = ""

                condition = self.rng.choice(conditions)
                contact_methods = [self.rng.choice(contact_methods_all)]
                if self.rng.random() < 0.4:
                    second = self.rng.choice(contact_methods_all)
                    if second not in contact_methods:
                        contact_methods.append(second)

                needs_phone = any(
                    m in ("phone_call", "whatsapp") for m in contact_methods
                )
                contact_number = (
                    f"090{self.rng.randint(10000000, 99999999)}"
                    if needs_phone
                    else ""
                )

                price = Decimal(str(get_price(category, sub_category)))
                is_sold = index == per_user - 1 and per_user >= 4
                is_expired = index == per_user - 2 and per_user >= 6
                promoted = index < 2 and self.rng.random() < 0.5

                # Temu-style discounts: ~40% of unsold listings have an
                # original price 10-35% above the sale price.
                original_price = None
                if not is_sold and self.rng.random() < 0.4:
                    markup = self.rng.uniform(1.10, 1.35)
                    original_price = (price * Decimal(str(markup))).quantize(
                        Decimal("1")
                    )

                product, was_created = Product.objects.get_or_create(
                    product_user=seller,
                    product_name=name,
                    category=category,
                    sub_category=sub_category,
                    defaults={
                        "category_obj": categories.get(category),
                        "subcategory_obj": next(
                            (s for s in subcategories.get(category, [])
                             if s.slug == sub_category.replace("_", "-")),
                            None,
                        ),
                        "state_obj": next(
                            (st for st in states_list if st.slug == state_slug),
                            None,
                        ),
                        "city_obj": next(
                            (c for c in cities.get(state_slug) or []
                             if c.slug == city_slug.replace("_", "-")),
                            None,
                        ),
                        "description": generate_description(
                            name, category, sub_category, condition
                        ),
                        "price": price,
                        "original_price": original_price,
                        "sold_count": self.rng.randint(0, 60) if not is_sold else self.rng.randint(1, 5),
                        "condition": condition,
                        "color": self.rng.choice(COLORS),
                        "quantity": (
                            1
                            if category in ("real_estate", "jobs", "services")
                            else self.rng.randint(1, 5)
                        ),
                        "negotiable": self.rng.choice([True, False]),
                        "state": state_slug,
                        "city": city_slug,
                        "contact_methods": contact_methods,
                        "contact_number": contact_number,
                        "active": not is_sold,
                        "sold": is_sold,
                        "promoted": promoted,
                        "delivery_available": self.rng.choice([True, False]),
                        "expires_at": (
                            timezone.now() - timedelta(days=2)
                            if is_expired
                            else timezone.now() + timedelta(days=30)
                        ),
                    },
                )
                products.append(product)

                # Backfill FKs for products seeded before the cutover.
                if not was_created and (
                    product.category_obj_id is None
                    or product.state_obj_id is None
                ):
                    product.category_obj = categories.get(category) or product.category_obj
                    product.subcategory_obj = next(
                        (s for s in subcategories.get(category, [])
                         if s.slug == sub_category.replace("_", "-")),
                        product.subcategory_obj,
                    )
                    product.state_obj = next(
                        (st for st in states_list if st.slug == state_slug),
                        product.state_obj,
                    )
                    product.city_obj = next(
                        (c for c in cities.get(state_slug) or []
                         if c.slug == city_slug.replace("_", "-")),
                        product.city_obj,
                    )
                    product.save(update_fields=["category_obj", "subcategory_obj", "state_obj", "city_obj"])

                if was_created:
                    created += 1
                    if self.with_images:
                        attach_images_to_product(product)

        self.stdout.write(
            self.style.SUCCESS(
                f"Products: {created} new listings "
                f"({len(products)} total in seed set)."
            )
        )
        return products

    # -------------------------------------------------------------------------
    # Engagement
    # -------------------------------------------------------------------------

    def _seed_engagement(self, products, sellers, buyers):
        favorites = 0
        views = 0

        for buyer in buyers:
            for product in self.rng.sample(
                products, k=min(len(products), min(max(4, len(products) // 3), 15))
            ):
                if product.product_user_id == buyer.id:
                    continue
                if not product.favorites.filter(pk=buyer.pk).exists():
                    product.favorites.add(buyer)
                    favorites += 1
                if not product.views.filter(pk=buyer.pk).exists():
                    product.views.add(buyer)
                    views += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Engagement: {favorites} favorites, {views} product views."
            )
        )

    # -------------------------------------------------------------------------
    # Ratings
    # -------------------------------------------------------------------------

    def _seed_ratings(self, products, sellers, buyers):
        created = 0

        for product in products:
            if product.sold:
                continue
            # ~70% of active listings get 1-4 ratings from other users.
            if self.rng.random() >= 0.7:
                continue

            raters = self.rng.sample(
                sellers + buyers,
                k=min(len(sellers) + len(buyers), self.rng.randint(1, 4)),
            )
            for rater in raters:
                if rater.id == product.product_user_id:
                    continue
                # Skew positive like a real marketplace.
                value = self.rng.choices([5, 4, 3, 2, 1], weights=[45, 30, 12, 8, 5])[0]
                _, was_created = ProductRating.objects.get_or_create(
                    product=product,
                    user=rater,
                    defaults={"value": value},
                )
                created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"Ratings: {created} new product ratings."))

    # -------------------------------------------------------------------------
    # Conversations
    # -------------------------------------------------------------------------

    def _seed_conversations(self, products, sellers, buyers, count):
        sellable = [p for p in products if not p.sold]
        if not sellable:
            return

        conversations = 0
        messages = 0

        for index in range(count):
            product = self.rng.choice(sellable)
            buyer_candidates = [
                b for b in buyers if b.id != product.product_user_id
            ]
            if not buyer_candidates:
                continue

            buyer = self.rng.choice(buyer_candidates)
            conversation, created = Conversation.objects.get_or_create(
                product=product,
                buyer=buyer,
                seller=product.product_user,
            )

            # Always consume the same RNG draws so repeated runs pick the
            # same threads (idempotent seeding).
            conversation_count = self.rng.randint(3, 6)

            if created or not conversation.messages.exists():
                for message_index in range(conversation_count):
                    sender = buyer if message_index % 2 == 0 else product.product_user
                    Message.objects.create(
                        conversation=conversation,
                        sender=sender,
                        body=MESSAGE_TEMPLATES[
                            (index + message_index) % len(MESSAGE_TEMPLATES)
                        ],
                        read=message_index < conversation_count - 2,
                    )
                    messages += 1
                conversations += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Messaging: {conversations} new conversations, "
                f"{messages} new messages."
            )
        )

    # -------------------------------------------------------------------------
    # Reports & notifications
    # -------------------------------------------------------------------------

    def _seed_reports(self, products, buyers):
        created = 0
        targets = self.rng.sample(products, k=min(3, len(products)))

        reasons = ["scam", "wrong_category", "duplicate"]
        for index, product in enumerate(targets):
            candidate_buyers = [
                b for b in buyers if b.id != product.product_user_id
            ]
            if not candidate_buyers:
                continue

            reporter = self.rng.choice(candidate_buyers)
            _, was_created = ProductReport.objects.get_or_create(
                product=product,
                reporter=reporter,
                defaults={
                    "reason": reasons[index % len(reasons)],
                    "details": "Flagged by the seed command for moderation testing.",
                },
            )
            created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(f"Reports: {created} new abuse reports.")
        )

    def _seed_notifications(self, users):
        created = 0
        for user in users:
            if Notifications.objects.filter(
                user=user, notification_type="system_notification"
            ).exists():
                continue
            Notifications.objects.create(
                user=user,
                notification_type="system_notification",
                message=(
                    "Welcome to Naija-Bay! Complete your profile to build trust "
                    "with buyers and sellers."
                ),
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Notifications: {created} new notifications.")
        )

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def _summary(self):
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Seed summary"))
        self.stdout.write(f"  States:         {State.objects.count()}")
        self.stdout.write(f"  Cities:         {City.objects.count()}")
        self.stdout.write(f"  Categories:     {Category.objects.count()}")
        self.stdout.write(f"  Sub-categories: {SubCategory.objects.count()}")
        self.stdout.write(f"  Users:          {User.objects.count()}")
        self.stdout.write(f"  Stores:         {Store.objects.count()}")
        self.stdout.write(f"  Follows:        {Follow.objects.count()}")
        self.stdout.write(f"  Products:       {Product.objects.count()}")
        self.stdout.write(f"  Favorites:      {Product.favorites.through.objects.count()}")
        self.stdout.write(f"  Views:          {Product.views.through.objects.count()}")
        self.stdout.write(f"  Conversations:  {Conversation.objects.count()}")
        self.stdout.write(f"  Messages:       {Message.objects.count()}")
        self.stdout.write(f"  Reports:        {ProductReport.objects.count()}")
        self.stdout.write(f"  Ratings:        {ProductRating.objects.count()}")
        self.stdout.write(f"  Notifications:  {Notifications.objects.count()}")
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Seeding complete. All seed accounts are idempotent.")
        )
