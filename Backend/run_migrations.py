#!/usr/bin/env python
"""Run database migrations for NaijaBay local development.

Checks the database, generates migrations for local apps that need them, then
applies all pending migrations. Development/local databases only.

Usage:
    cd Backend
    python run_migrations.py
    python run_migrations.py --check-only     # report required changes, write nothing
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NaijaBay.settings")
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.db import connection  # noqa: E402

LOCAL_APPS = ("accounts", "core", "products", "messaging", "orders", "payments", "NaijaBay")


def check_environment():
    if getattr(settings, "ENVIRONMENT", None) != "development":
        raise SystemExit(
            "run_migrations.py is development-only; ENVIRONMENT="
            f"{getattr(settings, 'ENVIRONMENT', None)!r}."
        )
    db = settings.DATABASES.get("default", {})
    engine = (db.get("ENGINE") or "").lower()
    host = str(db.get("HOST") or "").lower()
    if not (engine.endswith("sqlite3") or host in {"", "localhost", "127.0.0.1", "::1"}):
        raise SystemExit("Refusing to run against a non-local database.")


def check_database():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("Database connection OK.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Manage NaijaBay migrations")
    parser.add_argument("--check-only", action="store_true", help="Only check for model changes")
    args = parser.parse_args()

    print("NaijaBay Migration Manager")
    print(f"Backend directory: {BACKEND_DIR}\n")

    check_environment()
    check_database()

    labels = [label for label in LOCAL_APPS if apps.is_installed(label)]
    print("Local apps:", ", ".join(labels))

    print("\nChecking for model changes...")
    call_command("makemigrations", *labels, check=True, dry_run=True, verbosity=1)
    if args.check_only:
        print("Check complete; nothing was written.")
        return

    print("\nGenerating migrations where needed...")
    call_command("makemigrations", *labels, verbosity=1)

    print("\nApplying pending migrations...")
    call_command("migrate", verbosity=1)
    print("\nMigration process completed.")


if __name__ == "__main__":
    main()
