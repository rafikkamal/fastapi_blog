# Enable forward references in type hints (lets you use classes before they are defined).
from __future__ import annotations

# ------------------------
# FastAPI Imports
# ------------------------

# Depends → used for dependency injection.
# HTTPException → used to raise HTTP errors (401, 403, etc.).
# status → constants for HTTP status codes.
from fastapi import Depends, HTTPException, status

# OAuth2PasswordBearer is a FastAPI helper dependency.
# It extracts the Bearer token from the "Authorization" header.
# Example header: Authorization: Bearer <token>
from fastapi.security import OAuth2PasswordBearer

# ------------------------
# Database Imports
# ------------------------

# select → used to build SQL SELECT queries.
from sqlalchemy import select

# AsyncSession → async DB session class from SQLAlchemy.
from sqlalchemy.ext.asyncio import AsyncSession

# ------------------------
# Project Imports
# ------------------------

# DB session dependency (yields AsyncSession).
from app.core.database import get_session

# decode_token → custom function to decode JWT and return the payload (claims).
from app.core.security import decode_token

# User model and UserRole enum (super_admin, editor, subscriber).
from app.models.user import User, UserRole


# ------------------------
# OAuth2 Scheme Setup
# ------------------------

# This tells FastAPI how to extract the token from requests.
# - tokenUrl is where clients get a token (our /auth/login endpoint).
# - Used automatically by Swagger UI's "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ------------------------
# Current User Dependency
# ------------------------

async def get_current_user(
    token: str = Depends(oauth2_scheme),          # Extract JWT from header
    db: AsyncSession = Depends(get_session)       # Inject DB session
) -> User:
    """
    Decode the JWT, fetch the user from the database, and return it.
    - Raises 401 if token is invalid or user is inactive/missing.
    """

    try:
        # Decode token payload (e.g., {"sub": "1", "role": "super_admin"})
        payload = decode_token(token)
        user_id = int(payload.get("sub"))

        # Build a SELECT query for User by id
        stmt = select(User).where(User.id == user_id)

        # Execute query
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()  # get user object or None
    except Exception:
        user = None  # On any error, treat as invalid

    # Reject if no user or inactive user
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return user  # return the User model object


# ------------------------
# Role-Based Access Dependency
# ------------------------

def require_roles(*roles: UserRole):
    """
    Dependency factory: ensures the current user has at least one of the given roles.

    Usage:
    @router.get("/admin-only")
    async def admin_endpoint(
        current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN))
    ):
        ...
    """

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        # If the user’s role is not in the allowed list → 403 Forbidden
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user  # otherwise return user object

    return checker
