"""Launch NaijaBay local development services.

This script is a launcher/supervisor only. It starts and monitors:
  1. React web development server (Vite, from Frontend/Web)
  2. Django ASGI server (Daphne) — HTTP API and WebSockets on one port

It does not run Django checks, create/apply migrations, seed data, run tests,
audit the project, or execute clean_project.py. Prepare the database with
``python run_migrations.py`` and ``python run_seed.py``.

Usage:
    cd Backend
    python run_server.py
    python run_server.py --no-frontend
    python run_server.py --preflight-only
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "Frontend" / "Web"
DJANGO_SETTINGS_MODULE = "NaijaBay.settings"
DJANGO_ASGI_APPLICATION = "NaijaBay.asgi:application"


@dataclass
class ManagedProcess:
    name: str
    process: subprocess.Popen
    cwd: Path
    command: list[str]


def format_command(cmd: list[str]) -> str:
    parts = []
    for part in cmd:
        if not part:
            parts.append('""')
        elif any(ch in part for ch in [' ', '\t', '"']):
            parts.append('"' + part.replace('"', '\\"') + '"')
        else:
            parts.append(part)
    return " ".join(parts)


def resolve_npm() -> str | None:
    for candidate in ("npm.cmd", "npm", "npm.exe"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def django_settings_or_exit():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    try:
        import django  # noqa: PLC0415

        django.setup()
        from django.conf import settings  # noqa: PLC0415

        return settings
    except Exception as exc:
        print(f"Failed to load Django settings ({DJANGO_SETTINGS_MODULE}): {exc}")
        print("Fix the environment/configuration and retry.")
        raise SystemExit(2) from exc


def start_process(name: str, cmd: list[str], cwd: Path) -> ManagedProcess:
    print(f"\n[{name}] starting")
    print(f"  cwd: {cwd}")
    print(f"  cmd: {format_command(cmd)}")
    env = os.environ.copy()
    kwargs: dict[str, object] = {"cwd": str(cwd), "env": env}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(cmd, **kwargs)  # type: ignore[arg-type]
    print(f"  pid: {process.pid}")
    return ManagedProcess(name=name, process=process, cwd=cwd, command=cmd)


def stop_process(managed: ManagedProcess, timeout: float = 8.0) -> None:
    proc = managed.process
    if proc.poll() is not None:
        return
    print(f"\n[{managed.name}] stopping (pid {proc.pid})...")
    try:
        if os.name == "nt":
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
                proc.wait(timeout=2.0)
            except Exception:
                proc.terminate()
        else:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except Exception:
                proc.terminate()
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                proc.kill()
            else:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except Exception:
                    proc.kill()
            proc.wait(timeout=5)
    except Exception as exc:
        print(f"[{managed.name}] stop error: {exc}")


def stop_all(processes: list[ManagedProcess]) -> None:
    if not processes:
        return
    order = {"Vite dev server": 0, "Daphne (ASGI)": 1}
    for managed in sorted(processes, key=lambda m: order.get(m.name, 99)):
        stop_process(managed)
    print("\nAll managed services stopped.")


def print_service_summary(started, blocked, host: str, port: str) -> None:
    print("\n" + "=" * 72)
    print("NaijaBay service status")
    print("=" * 72)
    for managed in started:
        print(f"STARTED  {managed.name} (pid {managed.process.pid})")
    for name, reason in blocked:
        print(f"BLOCKED  {name}: {reason}")
    print("\nEndpoints / notes:")
    print(f"  - Daphne (ASGI): http://{host}:{port} (HTTP API + WebSockets) when started")
    print("  - API docs: http://{0}:{1}/api/v1/docs/".format(host, port))
    print("  - Vite dev server: usually http://localhost:5173 (Vite may choose another port)")
    print("  - Prepare data first: python run_migrations.py && python run_seed.py")
    print("  - Press Ctrl+C in this terminal to stop all managed processes.")
    print("=" * 72 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch Vite and Daphne for local NaijaBay development."
    )
    parser.add_argument(
        "--host", default=os.environ.get("DJANGO_HOST", "127.0.0.1"),
        help="Host/interface for Daphne (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port", default=os.environ.get("DJANGO_PORT", "8000"),
        help="Port for Daphne (default: 8000)",
    )
    parser.add_argument("--no-frontend", action="store_true", help="Do not start the Vite dev server")
    parser.add_argument(
        "--preflight-only", action="store_true",
        help="Check prerequisites and print the launch plan without starting anything",
    )
    args = parser.parse_args()

    os.chdir(SCRIPT_DIR)
    print("=" * 72)
    print("NaijaBay development launcher")
    print("Launcher only: no checks, no migrations, no seeding, no tests, no cleanup.")
    print("=" * 72)
    print(f"Python: {sys.executable} ({sys.version.split()[0]})")
    print(f"Platform: {sys.platform}")
    print(f"Backend dir: {SCRIPT_DIR}")
    print(f"Frontend dir: {FRONTEND_DIR}")

    django_settings_or_exit()
    npm = resolve_npm()

    planned: list[tuple[str, list[str], Path]] = []
    blocked: list[tuple[str, str]] = []
    started: list[ManagedProcess] = []

    if not (FRONTEND_DIR / "package.json").exists() and not args.no_frontend:
        blocked.append(("Vite dev server", f"package.json not found at {FRONTEND_DIR / 'package.json'}."))

    try:
        if args.no_frontend:
            blocked.append(("Vite dev server", "skipped (--no-frontend)."))
        elif not (FRONTEND_DIR / "package.json").exists():
            pass
        elif npm is None:
            blocked.append(("Vite dev server", "npm not found on PATH (npm/npm.cmd/npm.exe)."))
        elif not (FRONTEND_DIR / "node_modules").exists():
            blocked.append(("Vite dev server", "Dependencies missing: run 'npm install' in Frontend/Web."))
        else:
            planned.append(("Vite dev server", [npm, "run", "dev"], FRONTEND_DIR))

        try:
            import daphne  # noqa: F401, PLC0415

            daphne_ok, daphne_reason = True, ""
        except Exception as exc:
            daphne_ok = False
            daphne_reason = f"daphne not importable ({exc.__class__.__name__}: {exc})."

        if daphne_ok:
            planned.append((
                "Daphne (ASGI)",
                [sys.executable, "-m", "daphne", "-b", str(args.host),
                 "-p", str(args.port), DJANGO_ASGI_APPLICATION],
                SCRIPT_DIR,
            ))
        else:
            blocked.append(("Daphne (ASGI)", daphne_reason))

        if args.preflight_only:
            print("\n" + "=" * 72)
            print("NaijaBay preflight plan")
            print("=" * 72)
            for name, cmd, cwd in planned:
                print(f"WOULD START  {name}: {format_command(cmd)} (cwd {cwd})")
            for name, reason in blocked:
                print(f"BLOCKED  {name}: {reason}")
            print("=" * 72 + "\n")
            print("Preflight only: nothing was started.")
            return 0

        started = [start_process(name, cmd, cwd) for name, cmd, cwd in planned]
        print_service_summary(started, blocked, str(args.host), str(args.port))
        if not started:
            print("No services were started. Resolve the blocked prerequisites and retry.")
            return 1

        while True:
            for managed in list(started):
                code = managed.process.poll()
                if code is None:
                    continue
                print(f"\n[{managed.name}] exited with code {code}.")
                started.remove(managed)
            if not started:
                print("All started services have exited.")
                return 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupt received. Stopping managed services...")
    except Exception as exc:
        print(f"\nLauncher runtime error: {exc}")
    finally:
        stop_all(started)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
