"""Seed marketplace categories and sub-categories.

Usage::

    python manage.py categories

The seeding logic lives in :func:`seed_categories` so that ``seed_all`` can
reuse it and both commands always produce identical rows.
"""

from django.core.management import BaseCommand

from core.models import Category, SubCategory
from NaijaBay.utils import SUBCATEGORY_MAP


def display_name(raw):
    """'phones_tablets' -> 'Phones Tablets'."""
    return raw.strip().title().replace("-", " ").replace("_", " ")


def seed_categories(command):
    """Create every category and sub-category from ``SUBCATEGORY_MAP`` (idempotent).

    Returns ``(categories, subcategories)``, both keyed by the raw category key.
    """
    categories = {}
    subcategories = {}
    new_categories = 0
    new_subcategories = 0

    for raw_category, raw_subs in SUBCATEGORY_MAP.items():
        if not raw_category:
            continue

        category, category_created = Category.objects.get_or_create(
            name=display_name(raw_category)
        )
        categories[raw_category] = category
        new_categories += int(category_created)

        subs = []
        for raw_sub in raw_subs:
            if not raw_sub or not raw_sub.strip():
                continue

            sub, sub_created = SubCategory.objects.get_or_create(
                category=category, name=display_name(raw_sub)
            )
            subs.append(sub)
            new_subcategories += int(sub_created)

        subcategories[raw_category] = subs

    command.stdout.write(
        command.style.SUCCESS(
            f"Categories: {new_categories} new categories, {new_subcategories} new "
            f"sub-categories ({len(categories)} / "
            f"{sum(len(v) for v in subcategories.values())} total)."
        )
    )
    return categories, subcategories


class Command(BaseCommand):
    help = "Generate categories and sub-categories (safe to run repeatedly)."

    def handle(self, *args, **options):
        seed_categories(self)
