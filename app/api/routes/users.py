# Enable forward references in type hints (allows referring to classes
# before they are defined elsewhere in the code).
from __future__ import annotations

# ------------------------
# FastAPI Imports
# ------------------------

# APIRouter → allows grouping endpoints by feature/module.
# Depends → dependency injection (injects DB sessions, current user, etc.).
# HTTPException → for throwing HTTP errors (404, 403, etc.).
# status → predefined HTTP status codes (400, 404, etc.).
from fastapi import APIRouter, Depends, HTTPException, status

# ------------------------
# Database Imports
# ------------------------

# AsyncSession → async database session from SQLAlchemy.
from sqlalchemy.ext.asyncio import AsyncSession

# select → SQLAlchemy function for building SELECT queries.
from sqlalchemy import select

# ------------------------
# Project Imports
# ------------------------

# Role-based access dependency. `require_roles(UserRole.SUPER_ADMIN)`
# ensures only super admins can access these endpoints.
from app.api.deps import require_roles

# Function to get a DB session (dependency for FastAPI).
from app.core.database import get_session

# User model and UserRole enum (super_admin, editor, subscriber).
from app.models.user import User, UserRole

# Pydantic schemas:
# - UserOut → what we return when sending user data to the client
# - UserUpdate → fields a super admin can update
from app.schemas.user import UserOut, UserUpdate


# ------------------------
# Router Setup
# ------------------------

# Create a router for all `/users` endpoints.
# These routes will appear under the "Users" tag in Swagger docs.
router = APIRouter(prefix="/users", tags=["Users"])


# ------------------------
# List Users Endpoint
# ------------------------

@router.get("/", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_session),  # Inject async DB session
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN)),  
    # 👆 Require that the current user has SUPER_ADMIN role.
):
    """
    Admin-only endpoint: List all users in the system.
    - Returns a list of UserOut objects
    - Only accessible to super admins
    """

    # Build and execute a SELECT query: SELECT * FROM users
    result = await db.execute(select(User))

    # scalars() → extracts rows into User model objects
    # all() → return as list
    return result.scalars().all()


# ------------------------
# Update User Endpoint
# ------------------------

@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,                         # Path param: ID of user to update
    payload: UserUpdate,                  # Request body: fields to update
    db: AsyncSession = Depends(get_session),  # Inject DB session
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN)),  
    # 👆 Only super admins can update users
):
    """
    Admin-only endpoint: Update a user by ID.
    - Allows updating full_name, role, and is_active
    - Returns the updated user
    """

    # Fetch user by primary key
    user = await db.get(User, user_id)

    # If not found, return 404 error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields only if present in the payload
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        # Ensure payload.role is converted to UserRole enum
        user.role = UserRole(payload.role)
    if payload.is_active is not None:
        user.is_active = payload.is_active

    # Commit changes to DB
    await db.commit()

    # Refresh user object from DB (e.g., get updated values, timestamps)
    await db.refresh(user)

    # Return updated user (serialized via UserOut schema)
    return user
