# Enable forward references in type hints (allows referencing classes not yet defined).
from __future__ import annotations

# ------------------------
# FastAPI & Security Imports
# ------------------------

# APIRouter → lets us group related endpoints into a modular router.
# Depends → used to inject dependencies (like DB session, current user, etc.).
# HTTPException → lets us throw HTTP errors with a code + message.
# status → contains constants for HTTP status codes (e.g., 400, 401, 201).
from fastapi import APIRouter, Depends, HTTPException, status

# OAuth2PasswordRequestForm is a FastAPI helper for login forms.
# It automatically parses `username` and `password` from form-data.
from fastapi.security import OAuth2PasswordRequestForm

# ------------------------
# Database & Models
# ------------------------

# AsyncSession → SQLAlchemy session class for async database operations.
from sqlalchemy.ext.asyncio import AsyncSession

# Dependency to fetch the currently authenticated user from JWT.
from app.api.deps import get_current_user

# Function that creates JWT access tokens.
from app.core.security import create_access_token

# CRUD layer for User model (encapsulates DB logic like get_by_email, create, authenticate).
from app.crud.crud_user import user_crud

# Dependency to get an async DB session from our sessionmaker.
from app.core.database import get_session

# Our User model and UserRole enum (super_admin, editor, subscriber).
from app.models.user import User, UserRole

# Pydantic schemas for request/response validation:
# - Token → for login response (access_token + token_type)
# - UserCreate → for registration payload
# - UserOut → for returning user info (safe fields, no password hash)
from app.schemas.user import Token, UserCreate, UserOut


# ------------------------
# Router Setup
# ------------------------

# Define a router for all authentication endpoints.
# Every endpoint here will be prefixed with `/auth` and tagged as "Auth" in OpenAPI docs.
router = APIRouter(prefix="/auth", tags=["Auth"])


# ------------------------
# Registration Endpoint
# ------------------------

@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Public endpoint: Register a new user.
    - Always creates a subscriber (cannot self-register as editor/super_admin).
    - Prevents duplicate emails.
    """
    # Check if email is already taken
    existing = await user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with default role = subscriber
    user = await user_crud.create(
        db,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=UserRole.subscriber,  # enforce default role
    )
    await db.commit()        # Save changes to DB
    await db.refresh(user)   # Refresh instance with values from DB (e.g., id)
    return user              # Returned as UserOut schema (no password_hash)


# ------------------------
# Login Endpoint
# ------------------------

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # parses form-data: username, password
    db: AsyncSession = Depends(get_session)            # inject DB session
):
    """
    Public endpoint: Log in with email + password.
    - Validates credentials
    - Returns a JWT access token if successful
    """

    # Treat OAuth2's "username" as "email"
    user = await user_crud.authenticate(
        db,
        email=form_data.username,
        password=form_data.password
    )

    # If no user found or password mismatch
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    # If user exists but is inactive
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Generate a JWT with subject = user.id and role = user.role
    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value
    )

    # Return token response { "access_token": "...", "token_type": "bearer" }
    return Token(access_token=access_token)


# ------------------------
# Me Endpoint
# ------------------------

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """
    Authenticated endpoint: Return details about the currently logged-in user.
    - Requires valid JWT Bearer token
    - Returns UserOut schema (id, email, full_name, role, is_active, etc.)
    """
    return current_user
