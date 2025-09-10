from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, email: str, full_name: str | None, password: str, role: UserRole) -> User:
        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            role=role,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        return user

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


user_crud = CRUDUser()
