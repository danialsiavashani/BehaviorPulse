"""
One-off script - NOT part of the deployed app. Deletes the junk user rows
pytest leaves behind in the dev DB. Every test file's _random_email()
generates addresses matching test_{8 hex chars}@example.com, and since
there's no separate test database or per-test rollback, every signup()
call in every test run leaves a permanent row. This clears those out - it
does NOT touch any account with a real email domain, yours included.

Usage (from backend/, with .venv active):
    python cleanup_test_users.py          # dry run, lists what it would delete
    python cleanup_test_users.py --yes    # actually deletes
"""
import re
import sys

from sqlalchemy import select

from app.api.routes.auth import _delete_user_and_all_data
from app.db.models.user import User
from app.db.session import SessionLocal

TEST_EMAIL_PATTERN = re.compile(r"^test_[0-9a-f]{8}@example\.com$")


def cleanup(confirm: bool) -> None:
    db = SessionLocal()
    try:
        all_users = db.scalars(select(User)).all()
        matches = [u for u in all_users if TEST_EMAIL_PATTERN.match(u.email)]

        print(f"{len(matches)} test users found out of {len(all_users)} total.")

        if not matches:
            return

        if not confirm:
            print("Dry run - no changes made. Re-run with --yes to actually delete.")
            return

        for user in matches:
            _delete_user_and_all_data(db, user)
        db.commit()
        print(f"Deleted {len(matches)} test users.")
    finally:
        db.close()


if __name__ == "__main__":
    cleanup(confirm="--yes" in sys.argv)