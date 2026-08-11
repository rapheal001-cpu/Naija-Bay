from django.core.management import BaseCommand
from core.models import Category, SubCategory
from NaijaBay.utils import SUBCATEGORY_MAP


class Command(BaseCommand):
    help = 'This Generate Categories and Sub categories.'

    def handle(self, *args, **options):
        total_categories = 0
        total_sub_categories = 0

        # Iterate over the original dictionary keys and values safely
        for original_category_name, sub_categories in SUBCATEGORY_MAP.items():
            category_name = original_category_name.strip().title().replace('_', ' ')

            if category_name:
                category, category_created = Category.objects.get_or_create(name=category_name)

                if category_created:
                    total_categories += 1
                    self.stdout.write(self.style.SUCCESS(f"Category '{category_name}' created."))
                else:
                    self.stdout.write(self.style.WARNING(f"Category '{category_name}' already exists."))

                # Process The Sub category
                for sub_category_name in sub_categories:
                    sub_category_name = sub_category_name.strip().title().replace('-', ' ').replace('_', ' ')

                    if sub_category_name:
                        # Pass the Category instance to the sub category model
                        sub_category, sub_category_created = SubCategory.objects.get_or_create(category=category, name=sub_category_name)

                        if sub_category_created:
                            total_sub_categories += 1
                            self.stdout.write(self.style.SUCCESS(f"  -> Subcategory '{sub_category_name}' created."))
                else:
                    self.stdout.write(self.style.WARNING(f"  -> City '{sub_category_name}' already exists."))

        self.stdout.write(self.style.SUCCESS(
            f"Finished! Total Category created: {total_categories}, Total Subcategory created: {total_sub_categories}."))
