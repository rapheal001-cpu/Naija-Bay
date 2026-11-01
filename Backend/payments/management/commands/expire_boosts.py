from django.core.management.base import BaseCommand

from payments.services import expire_boosts


class Command(BaseCommand):
    help = (
        "Switch off ad boosts whose time is up. Listing pages also do this lazily, "
        "but schedule this (cron / Render cron job, e.g. every 15 minutes) for certainty."
    )

    def handle(self, *args, **options):
        count = expire_boosts()
        self.stdout.write(self.style.SUCCESS(f"Expired {count} boost(s)."))
