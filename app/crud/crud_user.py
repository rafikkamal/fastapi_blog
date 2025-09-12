# Enable forward references in type hints (lets you use classes before they’re defined).
from __future__ import annotations

# ------------------------
# SQLAlchemy Imports
# ------------------------

# select → used to build SQL SELECT queries.
from sqlalchemy import select

# AsyncSession → async session class for DB operations.
from sqlalchemy.ext.asyncio import AsyncSession

# ------------------------
# Project Imports
# ------------------------

# Import the User model and UserRole enum (super_admin, editor, subscriber).
from app.models.user import User, UserRole

# Security helpers:
# - get_password_hash → hashes a plaintext password
# - verify_password → checks if a plaintext password matches a stored hash
from app.core.security import get_password_hash, verify_password


# ------------------------
# CRUD Class for User
# ------------------------

class CRUDUser:
    """
    Encapsulates all database operations for the User model.
    Keeps routes clean by hiding SQLAlchemy details behind helper methods.
    """

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """
        Find a user by email.
        - Returns User object if found, else None
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        """
        Find a user by ID.
        - Returns User object if found, else None
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        full_name: str | None,
        password: str,
        role: UserRole
    ) -> User:
        """
        Create a new user.
        - Hashes password before storing
        - Sets is_active = True
        - Does not commit (caller must commit)
        """
        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),  # hash plaintext
            role=role,
            is_active=True,
        )
        db.add(user)
        # flush() sends INSERT to DB so that `user.id` is available,
        # but doesn’t commit transaction yet.
        await db.flush()
        return user

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str
    ) -> User | None:
        """
        Verify user credentials.
        - Returns User if email exists and password matches
        - Returns None otherwise
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


# Instantiate a single CRUDUser object to be imported in routes.
user_crud = CRUDUser()
