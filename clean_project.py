#!/usr/bin/env python
"""Clean disposable build/cache/runtime artifacts for NaijaBay.

Dry-run by default. Re-run with --delete to actually remove targets.

Targets (same idea as SkillStream's clean_project.py, adapted to NaijaBay):
  Backend:  __pycache__, generated migration .py/.pyc files (except __init__.py),
            db.sqlite3 + sidecars/backups, logs/, staticfiles/, mediafiles/,
            .pytest_cache, .coverage, htmlcov
  Web:      dist/

Never touches source code outside generated migrations, .env files, virtual
environments, node_modules, .git, or anything outside the scoped targets.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "Backend"
FRONTEND_WEB_DIR = PROJECT_ROOT / "Frontend" / "Web"

SKIP_DIR_NAMES = {".git", ".hg", ".svn", ".venv", "venv", "env", "ENV", "node_modules"}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def under_skipped(path: Path, base: Path) -> bool:
    try:
        parts = path.relative_to(base).parts
    except ValueError:
        return True
    return any(part in SKIP_DIR_NAMES for part in parts)


def collect_targets():
    targets = {
        "pycache": [],
        "generated_migrations": [],
        "sqlite_files": [],
        "runtime_dirs": [],
        "extra_artifacts": [],
        "frontend_dist": [],
    }
    if BACKEND_DIR.exists():
        for current, dirnames, _files in os.walk(BACKEND_DIR, topdown=True):
            current_path = Path(current)
            kept = []
            for name in dirnames:
                child = current_path / name
                if name in SKIP_DIR_NAMES:
                    continue
                if name == "__pycache__":
                    targets["pycache"].append(child)
                    continue
                kept.append(name)
            dirnames[:] = kept

        for migrations_dir in BACKEND_DIR.rglob("migrations"):
            if not migrations_dir.is_dir() or under_skipped(migrations_dir, BACKEND_DIR):
                continue
            for item in migrations_dir.iterdir():
                if item.is_file() and item.name != "__init__.py" and item.suffix in {".py", ".pyc", ".pyo"}:
                    targets["generated_migrations"].append(item)

        for name in ("db.sqlite3", "db.sqlite3-journal", "db.sqlite3-wal", "db.sqlite3-shm"):
            path = BACKEND_DIR / name
            if path.exists():
                targets["sqlite_files"].append(path)
        targets["sqlite_files"].extend(sorted(BACKEND_DIR.glob("db.sqlite3.bak-*")))

        for name in ("logs", "staticfiles", "mediafiles"):
            path = BACKEND_DIR / name
            if path.is_dir() and not under_skipped(path, BACKEND_DIR):
                targets["runtime_dirs"].append(path)

        for name in (".pytest_cache", "htmlcov"):
            path = BACKEND_DIR / name
            if path.is_dir():
                targets["extra_artifacts"].append(path)
        coverage = BACKEND_DIR / ".coverage"
        if coverage.is_file():
            targets["extra_artifacts"].append(coverage)

    dist = FRONTEND_WEB_DIR / "dist"
    if dist.is_dir():
        targets["frontend_dist"].append(dist)

    for key, items in targets.items():
        targets[key] = sorted({p.resolve() for p in items}, key=str)
    return targets


def remove(path: Path):
    try:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()
        return True, None
    except OSError as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean NaijaBay build/cache artifacts")
    parser.add_argument("--delete", action="store_true", help="Actually delete (default: dry-run)")
    args = parser.parse_args()

    targets = collect_targets()
    sections = [
        ("__pycache__ directories", "pycache"),
        ("Generated migration files (keeps __init__.py)", "generated_migrations"),
        ("SQLite database/backups", "sqlite_files"),
        ("Runtime directories (logs/staticfiles/mediafiles)", "runtime_dirs"),
        ("Extra artifacts", "extra_artifacts"),
        ("Frontend/Web dist", "frontend_dist"),
    ]
    total = 0
    for title, key in sections:
        items = targets[key]
        if not items:
            continue
        print(f"[{title}]")
        for item in items:
            print(f"  - {'dir ' if item.is_dir() else 'file'}: {rel(item)}")
            total += 1
        print()

    if total == 0:
        print("Nothing to clean.")
        return 0
    if not args.delete:
        print(f"Dry run: {total} target(s). Re-run with --delete to remove them.")
        return 0

    failed = 0
    for _title, key in sections:
        for item in targets[key]:
            ok, error = remove(item)
            if not ok:
                print(f"FAILED: {rel(item)}: {error}")
                failed += 1
    print(f"Cleaned {total - failed}/{total} target(s).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
