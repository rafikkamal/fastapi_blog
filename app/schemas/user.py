# Enable forward references in type hints (lets you reference classes
# before they are defined).
from __future__ import annotations

# ------------------------
# Pydantic Imports
# ------------------------

# BaseModel → parent class for all schemas.
# EmailStr → type for validating email strings.
# Field → add extra validation (e.g., min/max length).
# ConfigDict → config for schema behavior (like ORM mode).
# field_validator → used to add custom validation logic to fields.
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

# Regex library (used for password strength checks).
import re

# Typing helpers:
# - Literal → restricts value to a specific set of strings.
# - Optional → marks fields that may be None or missing.
from typing import Literal, Optional


# ------------------------
# Token Schemas
# ------------------------

class Token(BaseModel):
    """
    Response schema for login endpoint.
    - access_token: the JWT string
    - token_type: always "bearer"
    """
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenPayload(BaseModel):
    """
    Internal schema for decoded JWT payload.
    - sub: subject (we store user id as string)
    - role: user role
    - exp: expiration timestamp (Unix epoch)
    """
    sub: str
    role: str
    exp: int


# ------------------------
# Base User Schema
# ------------------------

class UserBase(BaseModel):
    """
    Shared properties for user objects.
    Used as a parent schema for create, update, and output.
    """
    email: EmailStr   # validates format automatically
    full_name: Optional[str] = None
    is_active: bool = True
    role: Literal["super_admin", "editor", "subscriber"] = "subscriber"


# ------------------------
# User Create Schema
# ------------------------

class UserCreate(UserBase):
    """
    Schema for registering a new user.
    Extends UserBase by adding password field with validation.
    """
    password: str = Field(..., min_length=8, max_length=128)

    # Custom validator for password strength
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Ensure password contains:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one symbol
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[^\w\s]", v):
            raise ValueError("Password must contain at least one symbol.")
        return v


# ------------------------
# User Login Schema
# ------------------------

class UserLogin(BaseModel):
    """
    Schema for login requests.
    Matches OAuth2PasswordRequestForm which expects 'username' + 'password'.
    """
    username: EmailStr
    password: str


# ------------------------
# User Update Schema
# ------------------------

class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    - All fields are optional (PATCH behavior).
    """
    full_name: Optional[str] = None
    role: Optional[Literal["super_admin", "editor", "subscriber"]] = None
    is_active: Optional[bool] = None


# ------------------------
# User Output Schema
# ------------------------

class UserOut(UserBase):
    """
    Schema for returning user data to clients.
    Extends UserBase and includes id.
    Excludes sensitive fields like password_hash.
    """
    id: int

    # Allow creating schema objects directly from ORM models.
    # Example: UserOut.model_validate(user_db_object)
    model_config = ConfigDict(from_attributes=True)
