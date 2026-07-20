"""Vercel build step: migrate DB (and seed if empty). collectstatic is run by Vercel."""

from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    # Avoid interactive prompts during build
    os.environ.setdefault("DJANGO_DEBUG", "0")

    import django

    django.setup()

    from django.core.management import call_command
    from django.db import connection

    print("Running migrations…")
    call_command("migrate", interactive=False, verbosity=1)

    # Seed demo catalog once when there are no books (safe for cold first deploy)
    try:
        from catalog.models import Book
        from catalog.permissions import ensure_staff_profile
        from django.contrib.auth import get_user_model

        if Book.objects.count() == 0:
            print("Empty catalog — running seed_catalog…")
            call_command("seed_catalog", verbosity=1)
        else:
            print(f"Catalog already has {Book.objects.count()} books — skip seed.")

        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")
            username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
            print(f"Creating superuser “{username}”…")
            user = User.objects.create_superuser(
                username=username,
                email="admin@example.com",
                password=password,
            )
            profile = ensure_staff_profile(user)
            profile.can_manage_team = True
            profile.save()
    except Exception as exc:  # noqa: BLE001 — build should not hard-fail seed
        print(f"Seed/superuser step: {exc}", file=sys.stderr)

    # Touch connection so build fails loudly if DATABASE_URL is wrong
    connection.ensure_connection()
    print("Build step finished.")


if __name__ == "__main__":
    main()
