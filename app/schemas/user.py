from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re
from typing import Literal, Optional


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user id or email (we use user id as string)
    role: str
    exp: int


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    role: Literal["super_admin", "editor", "subscriber"] = "subscriber"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # At least one uppercase, one lowercase, one number, one symbol
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[^\w\s]", v):
            raise ValueError("Password must contain at least one symbol.")
        return v


class UserLogin(BaseModel):
    username: EmailStr  # OAuth2PasswordRequestForm uses 'username'
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Literal["super_admin", "editor", "subscriber"]] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
