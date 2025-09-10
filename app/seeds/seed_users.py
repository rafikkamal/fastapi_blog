from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole


SEED_USERS = [
    {
        "email": "admin@example.com",
        "full_name": "Super Admin",
        "password": "password123",
        "role": UserRole.SUPER_ADMIN,
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


async def seed_users():
    async with AsyncSessionLocal() as session:
        # Find which emails already exist (idempotent)
        emails = [u["email"] for u in SEED_USERS]
        result = await session.execute(select(User.email).where(User.email.in_(emails)))
        existing = {row[0] for row in result.all()}

        created = 0
        for u in SEED_USERS:
            if u["email"] in existing:
                continue
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                password_hash=get_password_hash(u["password"]),
                role=u["role"],
                is_active=u["is_active"],
            )
            session.add(user)
            created += 1

        if created:
            await session.commit()

        return {"created": created, "skipped": len(SEED_USERS) - created}


def main():
    res = asyncio.run(seed_users())
    print(f"Users created: {res['created']}, skipped (already existed): {res['skipped']}")


if __name__ == "__main__":
    main()
