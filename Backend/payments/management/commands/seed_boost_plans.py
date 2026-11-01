from decimal import Decimal

from django.core.management.base import BaseCommand

from payments.models import BoostPlan

# Starter plans only. Edit freely in the Django admin (Payments -> Boost plans).
# This command never overwrites a plan that already exists.
DEFAULT_PLANS = [
    {
        "slug": "basic", "name": "Basic Boost", "price": Decimal("1500.00"),
        "duration_days": 3, "boost_level": 1, "sort_order": 1,
        "description": "A quick visibility bump.",
        "benefits": ["Shown above regular listings for 3 days", "Boosted badge on your ad"],
    },
    {
        "slug": "standard", "name": "Standard Boost", "price": Decimal("3500.00"),
        "duration_days": 7, "boost_level": 2, "sort_order": 2,
        "description": "A full week at the top.",
        "benefits": ["Ranks above Basic boosts for 7 days", "Boosted badge on your ad", "Priority in search results"],
    },
    {
        "slug": "premium", "name": "Premium Boost", "price": Decimal("7500.00"),
        "duration_days": 14, "boost_level": 3, "sort_order": 3,
        "description": "Maximum exposure for two weeks.",
        "benefits": ["Top of every list for 14 days", "Boosted badge on your ad", "Priority in search results", "Best for high-value items"],
    },
]


class Command(BaseCommand):
    help = "Create the default ad boost plans (idempotent; existing plans are left untouched)."

    def handle(self, *args, **options):
        created = 0
        for plan in DEFAULT_PLANS:
            _, was_created = BoostPlan.objects.get_or_create(slug=plan["slug"], defaults=plan)
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Boost plans ready ({created} created)."))
