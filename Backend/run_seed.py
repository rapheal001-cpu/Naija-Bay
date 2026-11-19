"""Run approved database seed operations for NaijaBay development.

Idempotent: running it twice does not create duplicate records. Development and
local databases only. Paths are resolved relative to this file.

Usage:
    cd Backend
    python run_seed.py
    python run_seed.py --images        # generate placeholder product photos
    python run_seed.py --clear         # wipe seeded data first
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NaijaBay.settings")
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.db import connection  # noqa: E402


def check_environment():
    version = sys.version_info
    if version < (3, 10):
        raise SystemExit(f"Python 3.10+ required (found {version.major}.{version.minor}).")
    if not (BACKEND_DIR / "manage.py").exists():
        raise SystemExit(f"manage.py not found in {BACKEND_DIR}")
    if getattr(settings, "ENVIRONMENT", None) != "development":
        raise SystemExit(
            "run_seed.py is development-only; ENVIRONMENT="
            f"{getattr(settings, 'ENVIRONMENT', None)!r}."
        )
    db = settings.DATABASES.get("default", {})
    engine = (db.get("ENGINE") or "").lower()
    host = str(db.get("HOST") or "").lower()
    if not (engine.endswith("sqlite3") or host in {"", "localhost", "127.0.0.1", "::1"}):
        raise SystemExit("Refusing to seed a non-local database.")
    print(f"Environment check passed (db engine: {db.get('ENGINE')}).")


def check_database():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("Database check passed.")


def run_operation(name, **options):
    print(f"\n== Running {name} ==")
    try:
        call_command(name, **options)
        print(f"== {name} completed ==\n")
    except Exception as exc:
        raise SystemExit(f"{name} failed: {exc}") from exc


def main():
    parser = argparse.ArgumentParser(description="Seed NaijaBay development data")
    parser.add_argument("--images", action="store_true", help="Generate placeholder product photos")
    parser.add_argument("--clear", action="store_true", help="Clear seeded data before seeding")
    args = parser.parse_args()

    print("== NaijaBay Database Seed Script ==\n")
    check_environment()
    check_database()

    images = args.images

    # Dependency order: locations -> categories -> boost plans -> users ->
    # products -> broad social activity -> attribute definitions.
    if args.clear:
        run_operation("seed_all", clear=True, images=images)

    run_operation("nigeria_states")
    run_operation("categories")
    run_operation("seed_boost_plans")
    run_operation("create_user")
    run_operation("seed_products", images=images)
    run_operation("seed_all", images=images)
    run_operation("attribute_definitions")

    print("== All seed operations completed successfully ==\n")


if __name__ == "__main__":
    main()
