import io
import json
import random

from allauth.account.models import EmailAddress
from django.core.files.base import ContentFile
from django.core.management import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from accounts.models import User
from NaijaBay.utils import STATE_CITY_MAP

# =============================================================================
# AVATAR GENERATOR
# =============================================================================

AVATAR_BG_COLORS = [
    (241, 196, 15),
    (231, 76, 60),
    (52, 152, 219),
    (46, 204, 113),
    (155, 89, 182),
    (52, 73, 94),
    (230, 126, 34),
    (26, 188, 156),
    (149, 165, 166),
    (44, 62, 80),
]


def generate_avatar_image(username, size=400):
    """Generates a simple colored square avatar with the user's initial."""
    bg_color = random.choice(AVATAR_BG_COLORS)
    img = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    initial = (username[0] if username else "U").upper()

    try:
        font = ImageFont.truetype("arial.ttf", size // 2)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initial, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]

    draw.text((x, y), initial, fill="white", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer


def attach_avatar_to_user(user):
    """Generates and saves a placeholder avatar for the given user."""
    buffer = generate_avatar_image(user.username)
    filename = f"{user.username}-avatar.jpg"
    user.avatar.save(filename, ContentFile(buffer.read()), save=True)


# =============================================================================
# FAKE DATA
# =============================================================================

FIRST_NAMES = [
    "Chinedu", "Emeka", "Ifeanyi", "Obinna", "Chukwuma", "Tunde", "Femi",
    "Segun", "Kunle", "Damilola", "Adebayo", "Ibrahim", "Musa", "Abdullahi",
    "Yusuf", "Bello", "Sani", "Uche", "Nonso", "Kelechi", "Amaka", "Ngozi",
    "Chiamaka", "Ada", "Ifeoma", "Funke", "Bukola", "Folake", "Titilayo",
    "Aisha", "Fatima", "Zainab", "Hauwa", "Halima", "Blessing", "Grace",
    "Joy", "Peace", "Precious", "Esther", "Tope", "Seyi", "Dayo", "Wale",
    "Ebuka", "Tochi", "Ayo", "Kemi", "Sola", "Nkechi",
]

LAST_NAMES = [
    "Okafor", "Okeke", "Eze", "Nwosu", "Obi", "Nnamdi", "Adeyemi", "Balogun",
    "Ogunleye", "Adeleke", "Bakare", "Salami", "Lawal", "Abubakar", "Danjuma",
    "Garba", "Aliyu", "Umar", "Ibe", "Ojo", "Ade", "Afolabi", "Chukwu",
    "Nwachukwu", "Ekwueme", "Onyeka", "Akpan", "Udoh", "Effiong", "Etim",
    "Okoro", "Uzor", "Igwe", "Anyanwu", "Olawale", "Oladipo", "Ogundipe",
    "Mohammed", "Suleiman", "Yakubu",
]

STREETS = [
    "Adeniran Ogunsanya Street", "Allen Avenue", "Awolowo Road", "Broad Street",
    "Church Road", "Market Road", "Ahmadu Bello Way", "Station Road",
    "Independence Avenue", "Unity Road", "Hospital Road", "School Road",
    "Palm Avenue", "New Layout Road", "Airport Road",
]

PHONE_PREFIXES = ["701", "703", "706", "802", "803", "805", "806", "810", "813", "816", "903", "906"]


def build_users_data(count, used_usernames, used_emails):
    """Builds `count` unique user dicts, skipping any username/email already used."""
    states = [s for s in STATE_CITY_MAP.keys() if s]
    data = []
    attempts = 0

    while len(data) < count and attempts < count * 50:
        attempts += 1
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        suffix = random.randint(1, 999)

        username = f"{first}{last}{suffix}".lower()[:15]
        email = f"{first}.{last}{suffix}@gmail.com".lower()

        if username in used_usernames or email in used_emails:
            continue

        used_usernames.add(username)
        used_emails.add(email)

        state = random.choice(states)
        city = random.choice(STATE_CITY_MAP[state])
        phone = f"+234{random.choice(PHONE_PREFIXES)}{random.randint(0, 9999999):07d}"

        data.append(
            {
                "first_name": first,
                "last_name": last,
                "username": username,
                "email": email,
                "phone_number": phone,
                "state": state,
                "address": f"{random.randint(1, 120)} {random.choice(STREETS)}, {city}",
                "verified": random.random() < 0.4,
            }
        )

    return data


# =============================================================================
# COMMAND
# =============================================================================

ADMIN_DEFAULTS = {
    "first_name": "admin",
    "last_name": "user",
    "email": "admin@gmail.com",
    "username": "admin",
    "phone_number": "+2349162271251",
    "state": "lagos",
    "password": "OnlyGod1@",
}


class Command(BaseCommand):
    help = (
        "Seeds the database with users. By default it creates 50 users in total "
        "(1 admin superuser + 49 regular users). Use --count to change the total. "
        "Use --user with --email, --username, --password to create a single user instead."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Total number of users to create including the admin (default: 50, minimum: 50)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="Password123@",
            help="Password for the generated regular users (default: Password123@)",
        )
        parser.add_argument(
            "--user",
            action="store_true",
            help="Create a single regular user with --email, --username and --password",
        )
        parser.add_argument("--email", type=str, help="Email for single user (with --user)")
        parser.add_argument("--username", type=str, help="Username for single user (with --user)")

    # -------------------------------------------------------------------------
    # helpers
    # -------------------------------------------------------------------------
    def _finalize_user(self, user):
        """Attach avatar + verified allauth email address."""
        attach_avatar_to_user(user)
        EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={"verified": True, "primary": True},
        )

    def _summary(self, user, user_type):
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "avatar": user.avatar.url if user.avatar else None,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "date_joined": str(user.date_joined),
            "type": user_type,
        }

    def _create_admin(self):
        existing = User.objects.filter(email=ADMIN_DEFAULTS["email"]).first()
        if existing:
            self.stdout.write(self.style.WARNING("Admin already exists, skipping."))
            return None

        admin = User.objects.create_superuser(**ADMIN_DEFAULTS)
        admin.verified = True
        admin.save(update_fields=["verified"])
        self._finalize_user(admin)
        return admin

    # -------------------------------------------------------------------------
    # modes
    # -------------------------------------------------------------------------
    def _create_single_user(self, options):
        email = options.get("email")
        username = options.get("username")
        password = options.get("password")

        if not all([email, username, password]):
            self.stdout.write(
                self.style.ERROR(
                    "When using --user, you must provide --email, --username, and --password"
                )
            )
            return

        user = User.objects.create_user(email=email, username=username, password=password)
        self._finalize_user(user)
        self.stdout.write(
            self.style.SUCCESS(json.dumps(self._summary(user, "regular user"), indent=4))
        )

    def _seed_users(self, options):
        total = max(options["count"], 50)
        password = options["password"]

        used_usernames = set(User.objects.values_list("username", flat=True))
        used_emails = set(User.objects.values_list("email", flat=True))

        created_admin = self._create_admin()

        # Top up to `total` users so re-running the command is idempotent
        # instead of adding another batch every time.
        regular_needed = max(total - User.objects.count(), 0)
        if regular_needed == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Already have {User.objects.count()} users (target {total}); "
                    "no regular users created."
                )
            )

        users_data = build_users_data(regular_needed, used_usernames, used_emails)

        created_count = 0
        for item in users_data:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=item["email"],
                    username=item["username"],
                    password=password,
                    first_name=item["first_name"],
                    last_name=item["last_name"],
                    phone_number=item["phone_number"],
                    state=item["state"],
                    address=item["address"],
                    verified=item["verified"],
                )
                self._finalize_user(user)
            created_count += 1

        if created_admin:
            self.stdout.write(
                self.style.SUCCESS(json.dumps(self._summary(created_admin, "superuser"), indent=4))
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count} regular users"
                f"{' + 1 admin' if created_admin else ''}. "
                f"Total users in database: {User.objects.count()}"
            )
        )
        self.stdout.write(
            f"Admin login: {ADMIN_DEFAULTS['email']} / {ADMIN_DEFAULTS['password']}\n"
            f"Regular users password: {password}"
        )

    def handle(self, *args, **options):
        if options["user"]:
            self._create_single_user(options)
        else:
            self._seed_users(options)
