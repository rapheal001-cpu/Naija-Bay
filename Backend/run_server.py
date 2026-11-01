#!/usr/bin/env python
"""Makemigrations, migrate, seed everything, then start the Django development server.

Usage (from the Backend folder)::

    python run_server.py                    # migrate + seed + runserver
    python run_server.py --no-images        # skip product photos (faster)
    python run_server.py --clear            # wipe seeded data, then reseed
    python run_server.py --reset-db          # back up db.sqlite3 and start from scratch
    python run_server.py --skip-seed        # just makemigrations + migrate + runserver
    python run_server.py --port 9000        # custom port
    python run_server.py --host 0.0.0.0     # listen on all interfaces

All seed commands are idempotent, so running this repeatedly is safe.
"""

import argparse
import glob
import os
import shutil
import sys
from datetime import datetime

# Make sure imports resolve no matter where the script is launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NaijaBay.settings")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Migrate, seed the database and start the Django server."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", default="8000", help="Port (default: 8000)")
    parser.add_argument("--no-images", action="store_true", help="Skip generating product images (faster, less disk)")
    parser.add_argument("--clear", action="store_true", help="Clear seeded data before seeding")
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Back up db.sqlite3 (renamed with a timestamp) and start from a fresh database",
    )
    parser.add_argument("--skip-seed", action="store_true", help="Skip all seed commands")
    parser.add_argument("--skip-migrate", action="store_true", help="Skip running migrations")
    parser.add_argument("--noreload", action="store_true", help="Disable the auto-reloader")
    return parser.parse_args()


def step(title):
    print(f"\n==> {title}", flush=True)


def sqlite_path():
    """Path of the SQLite file, or None when another database is configured."""
    from django.conf import settings

    db = settings.DATABASES["default"]
    if "sqlite3" not in db["ENGINE"]:
        return None
    return str(db["NAME"])


def reset_database():
    from django.db import connections

    path = sqlite_path()
    if not path:
        print("--reset-db only works with SQLite; skipping.")
        return
    connections.close_all()
    if os.path.exists(path):
        backup = f"{path}.bak-{datetime.now():%Y%m%d-%H%M%S}"
        shutil.move(path, backup)
        print(f"Old database backed up to: {backup}")
    else:
        print("No existing database file; nothing to back up.")


def warn_if_stale_database():
    """No migration files + an old SQLite file usually means a mismatched schema."""
    path = sqlite_path()
    has_migrations = glob.glob(os.path.join(BASE_DIR, "*", "migrations", "0*.py"))
    if path and os.path.exists(path) and os.path.getsize(path) > 0 and not has_migrations:
        print(
            "\nWARNING: db.sqlite3 already exists but this project has no migration "
            "files yet.\nIf you see 'no such table' / 'no such column' errors, stop and "
            "re-run with:  python run_server.py --reset-db\n",
            flush=True,
        )


def seed(args):
    from django.core.management import call_command

    if args.reset_db:
        step("Resetting database")
        reset_database()
    else:
        warn_if_stale_database()

    if not args.skip_migrate:
        step("Creating migrations")
        call_command("makemigrations", interactive=False)

        step("Applying migrations")
        call_command("migrate", interactive=False)

    if args.skip_seed:
        return

    images = not args.no_images

    if args.clear:
        step("Clearing old seeded data")
        call_command("seed_all", clear=True, images=images)

    step("Seeding Nigerian states and cities")
    call_command("nigeria_states")

    step("Seeding categories and sub-categories")
    call_command("categories")

    step("Seeding admin and regular users (+ avatars and verified emails)")
    call_command("create_user")

    step("Giving every user a store and at least 3 products")
    call_command("seed_products", images=images)

    # Runs last on purpose: it adds sellers/buyers, stores, follows, products,
    # favorites, views, ratings, chats, reports and notifications across ALL
    # users and products created above.
    step("Seeding sellers, social activity, chats, ratings, reports and notifications")
    call_command("seed_all", images=images)


def main():
    args = parse_args()

    if os.environ.get("RUN_MAIN") != "true" and not os.path.exists(
        os.path.join(BASE_DIR, ".env")
    ):
        print(
            "\nWARNING: Backend/.env not found. Without it DEBUG is off and every "
            "request is rejected.\nCopy .env.example to .env first:  copy .env.example .env\n",
            flush=True,
        )

    import django

    django.setup()

    # The auto-reloader re-runs this script in a child process; only seed once.
    if os.environ.get("RUN_MAIN") != "true":
        try:
            seed(args)
        except Exception as exc:
            print(f"\nSeeding failed: {exc}", file=sys.stderr)
            raise

    step(f"Starting server at http://{args.host}:{args.port}/")
    from django.core.management import call_command

    call_command(
        "runserver",
        f"{args.host}:{args.port}",
        use_reloader=not args.noreload,
    )


if __name__ == "__main__":
    main()
