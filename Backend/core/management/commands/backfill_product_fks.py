"""Backfill the relational FKs on Product from the legacy string fields.

Usage::

    python manage.py backfill_product_fks --dry-run   # report mapping only, zero writes
    python manage.py backfill_product_fks             # apply (requires approval)

Mapping rules mirror the serializers: the legacy strings store underscore keys
(``phones_tablets``) while the taxonomy tables store hyphenated slugs
(``phones-tablets``), so every value is normalized with ``replace('_', '-')``.

Products whose values cannot be resolved are reported and left untouched — the
command never guesses, and it aborts before applying anything if any product
is unmapped (unless ``--allow-partial`` is passed).
"""

from django.core.management import BaseCommand, CommandError
from django.db import transaction

from core.models import Category, City, State, SubCategory
from products.models import Product


def _slug(value):
    return str(value).strip().lower().replace("_", "-").replace(" ", "-")


def _loose_slug(value):
    """Punctuation-insensitive key (``Jama'are``/``kolokuma_opokuma`` both sides)."""
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def resolve_fk(value, model, **scope_filters):
    """Resolve one legacy string value to a taxonomy row (or None)."""
    if not value:
        return None
    qs = model.objects.filter(slug=_slug(value), **scope_filters)
    return qs.first()


def check_city_belongs(state, city):
    return bool(state and city and city.state_id == state.id)


def plan_backfill():
    """Compute the FK plan for every product. Returns (plan, unresolved)."""
    plan = []
    unresolved = []

    categories = {c.slug: c for c in Category.objects.all()}
    subcats = {}  # (category_id, slug) -> sub, keyed by hyphenated + loose forms
    states = {}
    state_loose = {}
    cities = {}   # (state_id, loose slug) -> city

    for s in State.objects.all():
        states[s.slug] = s
        state_loose.setdefault(_loose_slug(s.slug), s)

    for sub in SubCategory.objects.select_related("category").all():
        subcats[(sub.category_id, sub.slug)] = sub
        subcats[(sub.category_id, _loose_slug(sub.slug))] = sub
    for city in City.objects.select_related("state").all():
        cities[(city.state_id, _loose_slug(city.slug))] = city

    def resolve_state(value):
        if not value:
            return None
        return states.get(value.strip().lower()) or state_loose.get(_loose_slug(value))

    for product in Product.objects.all().order_by("id"):
        target = {"product": product}
        problems = []

        cat = categories.get(_slug(product.category)) if product.category else None
        if product.category and cat is None:
            problems.append(f"category '{product.category}'")
        target["category_obj"] = cat

        sub = None
        if cat and product.sub_category:
            sub = subcats.get((cat.id, _slug(product.sub_category))) or subcats.get((cat.id, _loose_slug(product.sub_category)))
            if sub is None:
                problems.append(f"sub_category '{product.sub_category}' not in '{cat.name}'")
        target["subcategory_obj"] = sub

        state = resolve_state(product.state)
        if product.state and state is None:
            problems.append(f"state '{product.state}'")
        target["state_obj"] = state

        city = None
        if state and product.city:
            city = cities.get((state.id, _loose_slug(product.city)))
            if city is None:
                problems.append(f"city '{product.city}' not in '{state.name}'")
        target["city_obj"] = city

        if problems:
            unresolved.append((product, problems))
        else:
            plan.append(target)

    return plan, unresolved


class Command(BaseCommand):
    help = "Backfill Product category/location FKs from legacy string fields (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Report mapping only; write nothing.")
        parser.add_argument("--allow-partial", action="store_true",
                            help="Apply resolvable rows even when some products are unmapped.")

    def handle(self, *args, **options):
        plan, unresolved = plan_backfill()

        self.stdout.write(f"Total products: {Product.objects.count()}")
        self.stdout.write(f"Fully resolvable: {len(plan)}")
        for product, problems in unresolved:
            self.stdout.write(self.style.ERROR(
                f"UNMAPPED id={product.id} '{product.product_name}': {', '.join(problems)}"
            ))

        if unresolved and not options["allow_partial"]:
            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("Dry run complete. Real run would abort; resolve unmapped values first."))
            else:
                raise CommandError("Unmapped products found. Re-run with --allow-partial to skip them.")
            return

        if options["dry_run"]:
            for target in plan[:5]:
                p = target["product"]
                self.stdout.write(
                    f"  [would set] id={p.id}: category={target['category_obj']}, "
                    f"sub={target['subcategory_obj']}, state={target['state_obj']}, city={target['city_obj']}"
                )
            if len(plan) > 5:
                self.stdout.write(f"  ... and {len(plan) - 5} more")
            self.stdout.write(self.style.WARNING("Dry run complete. No rows were written."))
            return

        updated = 0
        with transaction.atomic():
            for target in plan:
                p = target["product"]
                changed = False
                for field in ("category_obj", "subcategory_obj", "state_obj", "city_obj"):
                    if getattr(p, field) != target[field]:
                        setattr(p, field, target[field])
                        changed = True
                if changed:
                    p.save(update_fields=["category_obj", "subcategory_obj", "state_obj", "city_obj"])
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"Backfill complete: {updated} products updated, {len(unresolved)} skipped."))
