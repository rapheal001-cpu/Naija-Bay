"""Seed Nigerian states and cities.

Usage::

    python manage.py nigeria_states

The seeding logic lives in :func:`seed_locations` so that ``seed_all`` can reuse
it and both commands always produce identical rows (no duplicate states/cities).
"""

from django.core.management import BaseCommand

from core.models import City, State
from NaijaBay.utils import STATE_CITY_MAP

STATE_NAME_OVERRIDES = {
    "fct": "FCT",
}


def state_display_name(state_slug):
    """'akwa_ibom' -> 'Akwa Ibom', 'fct' -> 'FCT'."""
    if state_slug in STATE_NAME_OVERRIDES:
        return STATE_NAME_OVERRIDES[state_slug]
    return state_slug.strip().replace("_", " ").title()


def get_or_create_state(state_slug):
    """Find a state by slug (or name, for older rows) or create it.

    Returns ``(state, created)``.
    """
    name = state_display_name(state_slug)

    state = (
        State.objects.filter(slug=state_slug).first()
        or State.objects.filter(name=name).first()
    )
    if state:
        return state, False

    return State.objects.create(name=name, slug=state_slug), True


def seed_locations(command):
    """Create every state and city from ``STATE_CITY_MAP`` (idempotent).

    Returns ``(states, cities)`` where ``cities`` maps state slug -> [City].
    """
    states = []
    cities = {}
    new_states = 0
    new_cities = 0

    for state_slug, city_names in STATE_CITY_MAP.items():
        if not state_slug:
            continue

        state, state_created = get_or_create_state(state_slug)
        states.append(state)
        new_states += int(state_created)

        city_objects = []
        for city_name in city_names:
            city_name = city_name.strip()
            if not city_name:
                continue

            city, city_created = City.objects.get_or_create(
                state=state, name=city_name
            )
            city_objects.append(city)
            new_cities += int(city_created)

        cities[state_slug] = city_objects

    command.stdout.write(
        command.style.SUCCESS(
            f"Locations: {new_states} new states, {new_cities} new cities "
            f"({len(states)} states / {sum(len(v) for v in cities.values())} cities total)."
        )
    )
    return states, cities


class Command(BaseCommand):
    help = "Generate Nigerian states and cities (safe to run repeatedly)."

    def handle(self, *args, **options):
        seed_locations(self)
