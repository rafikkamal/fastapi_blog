# Enable forward references in type hints (lets you reference classes before they are defined).
from __future__ import annotations

# asyncio is needed because our DB operations are async (AsyncSession).
import asyncio

# SQLAlchemy SELECT function (for querying).
from sqlalchemy import select

# Import AsyncSessionLocal factory from our database config.
# This creates async sessions connected to our Postgres DB.
from app.core.database import AsyncSessionLocal

# Password hashing function (so we never store plaintext passwords).
from app.core.security import get_password_hash

# Import User model and UserRole enum.
from app.models.user import User, UserRole


# ------------------------
# Seed Data (Default Users)
# ------------------------

# A list of dictionaries representing users we want to insert if missing.
SEED_USERS = [
    {
        "email": "admin@example.com",
        "full_name": "Super Admin",
        "password": "password123",        # Will be hashed before saving
        "role": UserRole.SUPER_ADMIN,     # role: super_admin
        "is_active": True,
    },
    {
        "email": "editor@example.com",
        "full_name": "Editor One",
        "password": "password123",
        "role": UserRole.EDITOR,
        "is_active": True,
    },
    {
        "email": "subscriber@example.com",
        "full_name": "Subscriber One",
        "password": "password123",
        "role": UserRole.SUBSCRIBER,
        "is_active": True,
    },
]


# ------------------------
# Seeder Logic
# ------------------------

async def seed_users():
    """
    Insert default users into the database if they don’t already exist.
    - Uses AsyncSessionLocal for DB access
    - Skips users that already exist (idempotent)
    """
    async with AsyncSessionLocal() as session:
        # Collect all seed emails into a list
        emails = [u["email"] for u in SEED_USERS]

        # Query DB for existing emails
        result = await session.execute(
            select(User.email).where(User.email.in_(emails))
        )
        # Put existing emails into a set for quick lookup
        existing = {row[0] for row in result.all()}

        created = 0  # counter for how many users are created

        # Iterate over SEED_USERS
        for u in SEED_USERS:
            if u["email"] in existing:
                # Skip if already exists
                continue

            # Create new User model object
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                # Store password as hash (never plaintext!)
                password_hash=get_password_hash(u["password"]),
                role=u["role"],
                is_active=u["is_active"],
            )
            session.add(user)
            created += 1

        # Only commit if at least one new user was added
        if created:
            await session.commit()

        # Return summary (for CLI or logs)
        return {"created": created, "skipped": len(SEED_USERS) - created}


# ------------------------
# Entrypoint
# ------------------------

def main():
    """
    Entrypoint to run seeding synchronously from CLI.
    Wraps the async function in asyncio.run().
    """
    res = asyncio.run(seed_users())
    print(
        f"Users created: {res['created']}, skipped (already existed): {res['skipped']}"
    )


# If file is executed directly (python -m app.seeds.seed_users),
# run the main() function.
if __name__ == "__main__":
    main()
