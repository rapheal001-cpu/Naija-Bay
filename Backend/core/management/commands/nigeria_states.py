from django.core.management import BaseCommand
from core.models import State, City
from NaijaBay.utils import STATE_CITY_MAP


class Command(BaseCommand):
    help = "This will Generate Nigeria States and Cities."

    def handle(self, *args, **options):
        total_states = 0
        total_cities = 0

        # Iterate over the original dictionary keys and values safely
        for original_state_name, cities in STATE_CITY_MAP.items():
            state_name = original_state_name.strip().title().replace('_', ' ')

            if state_name:
                # Get or create the State instance
                state, state_created = State.objects.get_or_create(name=state_name)

                if state_created:
                    total_states += 1
                    self.stdout.write(self.style.SUCCESS(f"State '{state_name}' created."))
                else:
                    self.stdout.write(self.style.WARNING(f"State '{state_name}' already exists."))

                # Process The Cities For the State
                for city_name in cities:
                    city_name = city_name.strip().title().replace('-', ' ').replace('_', ' ')

                    if city_name:
                        # Pass the State instance to the city model
                        city, city_created = City.objects.get_or_create(state=state, name=city_name)

                        if city_created:
                            total_cities += 1
                            self.stdout.write(self.style.SUCCESS(f"  -> City '{city_name}' created."))
                else:
                    self.stdout.write(self.style.WARNING(f"  -> City '{city_name}' already exists."))

        self.stdout.write(self.style.SUCCESS(
            f"Finished! Total States created: {total_states}, Total Cities created: {total_cities}."))
