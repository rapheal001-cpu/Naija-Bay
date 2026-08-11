import json
from django.core.management import BaseCommand
from accounts.models import User
from allauth.account.models import EmailAddress


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
            first_name = 'admin'
            last_name = 'user'
            email = "admin@gmail.com"
            username = "admin"
            phone_number = '09162271251'
            state = 'lagos'
            password = "OnlyGod1@"
            user = User.objects.create_superuser(
               first_name=first_name, last_name=last_name, email=email, username=username, phone_number=phone_number, state=state, password=password
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
            EmailAddress.objects.create(
                user=user, email=user.email, verified=True, primary=True
            )

            context = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
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
