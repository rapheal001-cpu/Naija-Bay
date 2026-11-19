"""Seed realistic products for every active user (or one user with --username).

The shared catalog, pricing and image helpers now live in private modules
`_catalog.py` and `_images.py` (same organisation as the SkillStream seeds).
"""

import random
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from accounts.models import Store, User
from core.models import Category, City, State, SubCategory
from NaijaBay.utils import (
    CATEGORY_CHOICES,
    SUBCATEGORY_MAP,
    CONDITION_CHOICES,
    CONTACT_METHOD_CHOICES,
    STATE_CHOICES,
    STATE_CITY_MAP,
    _city_slug,
)
from products.models import Product

from ._catalog import (
    MIN_PRODUCTS_PER_USER,
    PRODUCT_CATALOG,
    COLORS,
    generate_description,
    get_price,
)
from ._images import attach_images_to_product


# =============================================================================
# COMMAND
# =============================================================================

class Command(BaseCommand):
    help = (
        "Seed realistic products for every active user (or one user with --username). "
        "Each user is topped up to at least 3 products, and gets a store if missing. "
        "Safe to run repeatedly."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Only seed this user (default: every active user)",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=MIN_PRODUCTS_PER_USER,
            help=(
                "Products each user should have, topping up what they already "
                f"have (default and minimum: {MIN_PRODUCTS_PER_USER})"
            ),
        )
        parser.add_argument(
            "--images",
            action="store_true",
            help="Generate 6-10 placeholder images per product (slower)",
        )
        parser.add_argument(
            "--no-store",
            action="store_true",
            help="Do not create stores for users that have none",
        )

    def handle(self, *args, **options):
        target = max(options["count"], MIN_PRODUCTS_PER_USER)

        if options["username"]:
            users = list(User.objects.filter(username=options["username"]))
            if not users:
                raise CommandError(f'User "{options["username"]}" does not exist.')
        else:
            users = list(User.objects.filter(is_active=True).order_by("id"))
            if not users:
                raise CommandError(
                    "No users found. Run `python manage.py create_user` first."
                )

        stores_created = 0
        products_created = 0
        images_filled = 0

        for user in users:
            if not options["no_store"]:
                stores_created += int(self._ensure_store(user))

            existing = Product.objects.filter(product_user=user).count()
            needed = max(target - existing, 0)
            if needed:
                products_created += self._create_products(
                    user, needed, options["images"]
                )

            # Give any existing product that still has no photos some images.
            if options["images"]:
                for product in Product.objects.filter(
                    product_user=user, images__isnull=True
                ):
                    attach_images_to_product(product)
                    images_filled += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Products: {products_created} new products across {len(users)} users "
                f"(each now has at least {target}); {stores_created} new stores; "
                f"{images_filled} older products received images."
            )
        )

    def _ensure_store(self, user):
        """Create a store for the user when they don't have one. Returns True if created."""
        if Store.objects.filter(user=user).exists():
            return False

        display = user.full_name
        name = f"{display} Store"[:60]
        if Store.objects.filter(name=name).exists():
            name = f"{name[:40]} ({user.username})"[:60]

        Store.objects.create(
            user=user,
            name=name,
            description=(
                f"{display} is a trusted Naija-Bay seller offering quality "
                "products with fast replies and safe delivery."
            ),
            verified=bool(getattr(user, "verified", False)),
            state=getattr(user, "state", "") or "",
            address=getattr(user, "address", "") or "",
        )
        return True

    def _create_products(self, user, count, with_images):
        categories = [c[0] for c in CATEGORY_CHOICES if c[0]]
        states = [s[0] for s in STATE_CHOICES if s[0]]
        conditions = [c[0] for c in CONDITION_CHOICES if c[0]]
        contact_methods_all = [m[0] for m in CONTACT_METHOD_CHOICES if m[0]]

        created = 0
        used_combinations = set()

        for i in range(count):
            category = random.choice(categories)
            while category not in PRODUCT_CATALOG:
                category = random.choice(categories)

            subcats = list(PRODUCT_CATALOG[category].keys())
            sub_category = random.choice(subcats)

            names = PRODUCT_CATALOG[category][sub_category]
            name = random.choice(names)

            combo_key = (category, sub_category, name)
            if combo_key in used_combinations and len(used_combinations) < count * 2:
                name = f"{name} - {random.choice(['Premium', 'Original', '2024 Model', 'Grade A', 'Direct UK'])}"
            used_combinations.add(combo_key)

            state = random.choice(states)
            city_names = [c for c in STATE_CITY_MAP.get(state, []) if c]
            city = _city_slug(random.choice(city_names)) if city_names else ""

            condition = random.choice(conditions)

            contact_methods = [random.choice(contact_methods_all)]
            if random.random() < 0.4:
                second = random.choice(contact_methods_all)
                if second not in contact_methods:
                    contact_methods.append(second)

            needs_phone = any(m in contact_methods for m in ("phone_call", "whatsapp"))
            contact_number = (
                f"090{random.randint(10000000, 99999999)}" if needs_phone else ""
            )

            description = generate_description(name, category, sub_category, condition)

            price = get_price(category, sub_category)

            original_price = None
            if random.random() < 0.4:
                original_price = (
                    Decimal(str(price)) * Decimal(str(random.uniform(1.10, 1.35)))
                ).quantize(Decimal("1"))

            # Cutover: resolve relational FKs (run `categories` + `nigeria_states`
            # or `seed_all` first so the lookup tables exist).
            category_obj = Category.objects.filter(slug=category.replace("_", "-")).first()
            subcategory_obj = (
                SubCategory.objects.filter(
                    category=category_obj, slug=sub_category.replace("_", "-")
                ).first()
                if category_obj
                else None
            )
            state_obj = State.objects.filter(slug=state).first()
            city_obj = (
                City.objects.filter(state=state_obj, slug=city.replace("_", "-")).first()
                if state_obj and city
                else None
            )

            product = Product.objects.create(
                product_user=user,
                product_name=name,
                description=description,
                price=Decimal(str(price)),
                original_price=original_price,
                sold_count=random.randint(0, 60),
                category=category,
                sub_category=sub_category,
                category_obj=category_obj,
                subcategory_obj=subcategory_obj,
                state_obj=state_obj,
                city_obj=city_obj,
                condition=condition,
                color=random.choice(COLORS),
                quantity=(
                    random.randint(1, 5)
                    if category not in ["real_estate", "jobs", "services"]
                    else 1
                ),
                negotiable=(
                    random.choice([True, False])
                    if category not in ["real_estate", "jobs"]
                    else True
                ),
                state=state,
                city=city,
                contact_methods=contact_methods,
                contact_number=contact_number,
                active=True,
                sold=False,
            )

            if with_images:
                attach_images_to_product(product)

            created += 1

        return created
