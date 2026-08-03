"""
One-off script - NOT part of the deployed app, don't commit changes into
app/. Solves the bootstrap problem: the admin dashboard lets an admin
promote other users to admin, but the *first* admin has to come from
somewhere outside any HTTP-reachable path. Run this once, manually,
against your own account. Every admin after that is made through the
/admin/users dropdown by an existing admin - this script does not need
to run again in normal operation.

Usage (from backend/, with .venv active):
    python promote_admin.py you@example.com
"""
import sys

from sqlalchemy import select

from app.db.models.user import User
from app.db.session import SessionLocal


def promote_to_admin(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            print(f"No user found with email: {email}")
            return

        if user.role == "admin":
            print(f"{email} is already an admin.")
            return

        user.role = "admin"
        db.commit()
        print(f"{email} is now an admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py <email>")
        sys.exit(1)

    promote_to_admin(sys.argv[1])