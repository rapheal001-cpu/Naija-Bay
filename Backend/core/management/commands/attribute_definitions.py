"""Seed category-specific attribute definitions and their options.

Usage::

    python manage.py attribute_definitions
    python manage.py attribute_definitions --dry-run   # report only, no writes

Definitions live in ``ATTRIBUTE_MAP`` keyed by category slug (hyphenated, matching
``Category.slug``). An entry may also carry a ``sub_category`` to narrow the scope.
The command is idempotent: every row is created with ``get_or_create``.
"""

from django.core.management import BaseCommand

from core.models import AttributeDefinition, AttributeOption, Category, SubCategory


def _def(category, name, label, data_type, **extra):
    """Shorthand for one definition entry."""
    entry = {"category": category, "name": name, "label": label, "data_type": data_type}
    entry["options"] = extra.pop("options", [])
    entry.update(extra)
    return entry


ATTRIBUTE_MAP = [
    # ------------------------------------------------------------------
    # Vehicles
    # ------------------------------------------------------------------
    _def("vehicles", "make", "Make", "select", sub_category="cars", required=True, sort_order=1,
         options=[("toyota", "Toyota"), ("honda", "Honda"), ("lexus", "Lexus"), ("mercedes-benz", "Mercedes-Benz"),
                  ("bmw", "BMW"), ("hyundai", "Hyundai"), ("kia", "Kia"), ("nissan", "Nissan"), ("ford", "Ford"),
                  ("volkswagen", "Volkswagen"), ("audi", "Audi"), ("peugeot", "Peugeot"), ("innoson", "Innoson"),
                  ("other", "Other")]),
    _def("vehicles", "model", "Model", "text", sub_category="cars", required=True, sort_order=2),
    _def("vehicles", "year", "Year of Manufacture", "number", sub_category="cars", filterable=True, sortable=True,
         min_value=1990, max_value=2026, sort_order=3),
    _def("vehicles", "fuel_type", "Fuel Type", "select", sub_category="cars", sort_order=4,
         options=[("petrol", "Petrol"), ("diesel", "Diesel"), ("hybrid", "Hybrid"), ("electric", "Electric"), ("cng", "CNG")]),
    _def("vehicles", "transmission", "Transmission", "select", sub_category="cars", sort_order=5,
         options=[("automatic", "Automatic"), ("manual", "Manual")]),
    _def("vehicles", "mileage", "Mileage", "number", sub_category="cars", unit="km",
         filterable=True, sortable=True, min_value=0, sort_order=6),
    _def("vehicles", "body_type", "Body Type", "select", sub_category="cars", sort_order=7,
         options=[("suv", "SUV"), ("sedan", "Sedan"), ("hatchback", "Hatchback"), ("pickup", "Pickup"),
                  ("minivan", "Minivan"), ("convertible", "Convertible"), ("coupe", "Coupe"), ("other", "Other")]),
    _def("vehicles", "make", "Make", "select", sub_category="motorcycles", sort_order=1,
         options=[("honda", "Honda"), ("yamaha", "Yamaha"), ("kymco", "Kymco"), ("bajaj", "Bajaj"),
                  ("haoue", "Haojue"), ("tvx", "TVS"), ("other", "Other")]),
    _def("vehicles", "year", "Year of Manufacture", "number", sub_category="motorcycles", filterable=True, sort_order=2,
         min_value=1990, max_value=2026),
    _def("vehicles", "mileage", "Mileage", "number", sub_category="motorcycles", unit="km", filterable=True, sort_order=3),
    _def("vehicles", "make", "Make", "select", sub_category="trucks-buses", sort_order=1,
         options=[("volvo", "Volvo"), ("mercedes-benz", "Mercedes-Benz"), ("man", "MAN"), ("hino", "Hino"),
                  ("toyota", "Toyota"), ("other", "Other")]),
    # ------------------------------------------------------------------
    # Real Estate
    # ------------------------------------------------------------------
    _def("real-estate", "property_type", "Property Type", "select", sort_order=1,
         options=[("detached-house", "Detached House"), ("semi-detached", "Semi-Detached"), ("duplex", "Duplex"),
                  ("flat", "Flat"), ("terraced", "Terraced"), ("studio", "Studio"), ("room", "Room")]),
    _def("real-estate", "bedrooms", "Bedrooms", "number", filterable=True, sortable=True, min_value=1, sort_order=2),
    _def("real-estate", "bathrooms", "Bathrooms", "number", filterable=True, min_value=1, sort_order=3),
    _def("real-estate", "furnishing", "Furnishing", "select", sort_order=4,
         options=[("furnished", "Furnished"), ("semi-furnished", "Semi-Furnished"), ("unfurnished", "Unfurnished")]),
    _def("real-estate", "land_size", "Land Size", "number", sub_category="land-plots", unit="sqm",
         filterable=True, sort_order=1),
    _def("real-estate", "title", "Title", "select", sub_category="land-plots", sort_order=2,
         options=[("c-of-o", "C of O"), ("registered-survey", "Registered Survey"), ("governor-consent", "Governor's Consent"),
                  ("deed-of-assignment", "Deed of Assignment"), ("family-receipt", "Family Receipt")]),
    # ------------------------------------------------------------------
    # Phones & Tablets
    # ------------------------------------------------------------------
    _def("phones-tablets", "brand", "Brand", "select", sort_order=1,
         options=[("apple", "Apple"), ("samsung", "Samsung"), ("xiaomi", "Xiaomi"), ("infinix", "Infinix"),
                  ("tecno", "Tecno"), ("google", "Google"), ("oppo", "Oppo"), ("nokia", "Nokia"), ("lenovo", "Lenovo"),
                  ("other", "Other")]),
    _def("phones-tablets", "model", "Model", "text", sort_order=2),
    _def("phones-tablets", "storage", "Storage", "select", sort_order=3, options=[
        ("16gb", "16GB"), ("32gb", "32GB"), ("64gb", "64GB"), ("128gb", "128GB"),
        ("256gb", "256GB"), ("512gb", "512GB"), ("1tb", "1TB")]),
    _def("phones-tablets", "ram", "RAM", "select", sub_category="mobile-phones", sort_order=4, options=[
        ("2gb", "2GB"), ("3gb", "3GB"), ("4gb", "4GB"), ("6gb", "6GB"), ("8gb", "8GB"), ("12gb", "12GB"), ("16gb", "16GB")]),
    # ------------------------------------------------------------------
    # Electronics
    # ------------------------------------------------------------------
    _def("electronics", "brand", "Brand", "select", sort_order=1,
         options=[("apple", "Apple"), ("hp", "HP"), ("dell", "Dell"), ("lenovo", "Lenovo"), ("samsung", "Samsung"),
                  ("lg", "LG"), ("sony", "Sony"), ("hisense", "Hisense"), ("tcl", "TCL"), ("other", "Other")]),
    _def("electronics", "screen_size", "Screen Size", "number", sub_category="tvs", unit="inch",
         filterable=True, sort_order=2),
    _def("electronics", "smart_tv", "Smart TV", "boolean", sub_category="tvs", sort_order=3),
    _def("electronics", "processor", "Processor", "text", sub_category="laptops-computers", sort_order=2),
    _def("electronics", "ram", "RAM", "select", sub_category="laptops-computers", sort_order=3, options=[
        ("4gb", "4GB"), ("8gb", "8GB"), ("16gb", "16GB"), ("32gb", "32GB")]),
    # ------------------------------------------------------------------
    # Fashion
    # ------------------------------------------------------------------
    _def("fashion", "brand", "Brand", "text", sort_order=1),
    _def("fashion", "size", "Size", "select", sort_order=2,
         options=[("xs", "XS"), ("s", "S"), ("m", "M"), ("l", "L"), ("xl", "XL"), ("xxl", "XXL"),
                  ("uk-3", "UK 3"), ("uk-4", "UK 4"), ("uk-5", "UK 5"), ("uk-6", "UK 6"), ("uk-7", "UK 7"),
                  ("uk-8", "UK 8"), ("uk-9", "UK 9"), ("uk-10", "UK 10")]),
    # ------------------------------------------------------------------
    # Home & Garden
    # ------------------------------------------------------------------
    _def("home-garden", "material", "Material", "select", sub_category="furniture", sort_order=1,
         options=[("wood", "Wood"), ("metal", "Metal"), ("plastic", "Plastic"), ("fabric", "Fabric"),
                  ("glass", "Glass"), ("leather", "Leather"), ("other", "Other")]),
    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------
    _def("jobs", "job_type", "Job Type", "select", sort_order=1,
         options=[("full-time", "Full Time"), ("part-time", "Part Time"), ("contract", "Contract"),
                  ("internship", "Internship"), ("remote", "Remote")]),
    _def("jobs", "experience_years", "Years of Experience", "number", filterable=True, min_value=0, sort_order=2),
    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------
    _def("services", "experience_years", "Years of Experience", "number", filterable=True, min_value=0, sort_order=1),
    # ------------------------------------------------------------------
    # Animals & Pets
    # ------------------------------------------------------------------
    _def("animals-pets", "breed", "Breed", "text", sort_order=1),
    _def("animals-pets", "age_months", "Age", "number", unit="months", min_value=0, sort_order=2),
    # ------------------------------------------------------------------
    # Food & Agriculture
    # ------------------------------------------------------------------
    _def("food-agriculture", "weight", "Weight", "number", unit="kg", filterable=True, min_value=0, sort_order=1),
    # ------------------------------------------------------------------
    # Health & Beauty
    # ------------------------------------------------------------------
    _def("health-beauty", "brand", "Brand", "text", sort_order=1),
    # ------------------------------------------------------------------
    # Kids & Baby
    # ------------------------------------------------------------------
    _def("kids-baby", "age_range", "Age Range", "select", sort_order=1,
         options=[("0-12-months", "0–12 months"), ("1-3-years", "1–3 years"), ("4-6-years", "4–6 years"),
                  ("7-12-years", "7–12 years"), ("teens", "Teens")]),
    # ------------------------------------------------------------------
    # Sports & Outdoor
    # ------------------------------------------------------------------
    _def("sports-outdoor", "size", "Size", "select", sub_category="football", sort_order=1,
         options=[("size-3", "Size 3"), ("size-4", "Size 4"), ("size-5", "Size 5")]),
    # ------------------------------------------------------------------
    # Books, Music & Movies
    # ------------------------------------------------------------------
    _def("books-music-movies", "author", "Author", "text", sub_category="books-textbooks", sort_order=1),
    _def("books-music-movies", "format", "Format", "select", sub_category="books-textbooks", sort_order=2,
         options=[("hardcover", "Hardcover"), ("paperback", "Paperback"), ("ebook", "eBook"), ("audiobook", "Audiobook")]),
]


def seed_attribute_definitions(command, dry_run=False):
    """Create every definition + option (idempotent). Returns counts."""
    counts = {"definitions_created": 0, "definitions_existing": 0, "options_created": 0, "options_existing": 0, "skipped": []}

    category_cache = {}
    sub_cache = {}

    for entry in ATTRIBUTE_MAP:
        cat_slug = entry["category"]
        if cat_slug not in category_cache:
            category_cache[cat_slug] = Category.objects.filter(slug=cat_slug).first()
        category = category_cache[cat_slug]
        if category is None:
            counts["skipped"].append(f"{cat_slug}/{entry['name']}: category not found")
            continue

        sub = None
        sub_slug = entry.get("sub_category")
        if sub_slug:
            cache_key = (category.id, sub_slug)
            if cache_key not in sub_cache:
                sub_cache[cache_key] = SubCategory.objects.filter(category=category, slug=sub_slug).first()
            sub = sub_cache[cache_key]
            if sub is None:
                counts["skipped"].append(f"{cat_slug}/{sub_slug}/{entry['name']}: sub-category not found")
                continue

        defaults = {
            "label": entry["label"],
            "data_type": entry["data_type"],
            "required": entry.get("required", False),
            "filterable": entry.get("filterable", True),
            "sortable": entry.get("sortable", False),
            "unit": entry.get("unit", ""),
            "min_value": entry.get("min_value"),
            "max_value": entry.get("max_value"),
            "sort_order": entry.get("sort_order", 0),
        }
        lookup = {"category": category, "sub_category": sub, "slug": entry["name"]}

        if dry_run:
            label = f"{cat_slug}{('/' + sub_slug) if sub_slug else ''}/{entry['name']}"
            exists = AttributeDefinition.objects.filter(**lookup).exists()
            counts["definitions_existing" if exists else "definitions_created"] += 1
            for value, opt_label in entry["options"]:
                opt_exists = AttributeOption.objects.filter(definition__slug=entry["name"], definition__category=category, value=value).exists()
                counts["options_existing" if opt_exists else "options_created"] += 1
            command.stdout.write(f"  [would seed] {label} ({entry['data_type']})")
            continue

        definition, created = AttributeDefinition.objects.get_or_create(**lookup, defaults=defaults)
        counts["definitions_created" if created else "definitions_existing"] += 1

        for idx, (value, opt_label) in enumerate(entry["options"]):
            _, opt_created = AttributeOption.objects.get_or_create(
                definition=definition, value=value,
                defaults={"label": opt_label, "sort_order": idx},
            )
            counts["options_created" if opt_created else "options_existing"] += 1

    return counts


class Command(BaseCommand):
    help = "Seed category-specific attribute definitions and options (safe to run repeatedly)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Report what would be created; write nothing.")

    def handle(self, *args, **options):
        counts = seed_attribute_definitions(self, dry_run=options["dry_run"])
        verb = "would create" if options["dry_run"] else "created"
        self.stdout.write(
            self.style.SUCCESS(
                f"Definitions: {counts['definitions_created']} to {verb}, "
                f"{counts['definitions_existing']} already present. "
                f"Options: {counts['options_created']} to {verb}, "
                f"{counts['options_existing']} already present."
            )
        )
        for skipped in counts["skipped"]:
            self.stdout.write(self.style.WARNING(f"Skipped: {skipped}"))
