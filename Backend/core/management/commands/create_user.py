import io
import json
import random
from django.core.management import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from accounts.models import User
from allauth.account.models import EmailAddress

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
# COMMAND
# =============================================================================


class Command(BaseCommand):
    help = "Creates a user. Use --admin for superuser with defaults, or --user with --email, --username, --password."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--admin",
            action="store_true",
            help="Create a superuser with default credentials",
        )
        group.add_argument(
            "--user",
            action="store_true",
            help="Create a regular user with provided credentials",
        )

        parser.add_argument(
            "--email", type=str, help="Email for regular user (required with --user)"
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Username for regular user (required with --user)",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password for regular user (required with --user)",
        )

    def handle(self, *args, **options):
        if options["admin"]:
            first_name = "admin"
            last_name = "user"
            email = "admin@gmail.com"
            username = "admin"
            phone_number = "09162271251"
            state = "lagos"
            password = "OnlyGod1@"
            user = User.objects.create_superuser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                phone_number=phone_number,
                state=state,
                password=password,
            )
            user_type = "superuser"

        elif options["user"]:
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

            user = User.objects.create_user(
                email=email, username=username, password=password
            )
            user_type = "regular user"

        if user:
            # Generate and attach a placeholder avatar
            attach_avatar_to_user(user)

            EmailAddress.objects.create(
                user=user, email=user.email, verified=True, primary=True
            )

            context = {
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

            output_msg = json.dumps(context, indent=4)
            self.stdout.write(self.style.SUCCESS(output_msg))
        else:
            self.stdout.write(self.style.WARNING("User not created!"))
