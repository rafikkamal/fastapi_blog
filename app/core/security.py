# -----------------------------------------------------------------------------
# Enable forward references for type hints
# -----------------------------------------------------------------------------
# - Allows using types that are defined later in the file without quotes.
# - Mostly useful in Pydantic models; harmless here.
from __future__ import annotations


# -----------------------------------------------------------------------------
# Standard library imports
# -----------------------------------------------------------------------------
# - datetime: used for generating token expiration timestamps.
# - timedelta: to add minutes to the current time for expiry.
# - timezone: ensure we store expiry in UTC explicitly.
from datetime import datetime, timedelta, timezone

# - typing.Any: generic type for values where type is flexible.
# - typing.Optional: marks parameters that can be None.
from typing import Any, Optional


# -----------------------------------------------------------------------------
# Third-party libraries
# -----------------------------------------------------------------------------
# - jose.jwt: to encode/decode JSON Web Tokens (JWTs).
# - jose.JWTError: raised when decoding/validation fails.
from jose import jwt, JWTError

# - passlib.context.CryptContext: wrapper for password hashing algorithms.
#   Lets us easily hash/verify passwords with bcrypt (or switch algorithms later).
from passlib.context import CryptContext


# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
# - Import global settings (secret, algorithm, expiry time).
#   Settings are loaded from environment variables via pydantic_settings.
from app.core.settings import settings


# -----------------------------------------------------------------------------
# 1) Configure password hashing context
# -----------------------------------------------------------------------------
# - bcrypt is a secure one-way hash function designed for passwords.
# - deprecated="auto" means old hashes (if algorithm changes) can still be verified.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -----------------------------------------------------------------------------
# 2) Hash a plaintext password
# -----------------------------------------------------------------------------
# - Input: raw password string from user signup.
# - Output: bcrypt hashed version (safe to store in DB).
def get_password_hash(raw: str) -> str:
    return pwd_context.hash(raw)


# -----------------------------------------------------------------------------
# 3) Verify a password against its hash
# -----------------------------------------------------------------------------
# - Input: raw password (from login attempt) and stored bcrypt hash.
# - Output: True if they match, False otherwise.
def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


# -----------------------------------------------------------------------------
# 4) Create a JWT access token
# -----------------------------------------------------------------------------
# - subject: typically the user ID or email (string).
# - role: user role (super_admin, editor, subscriber).
# - expires_minutes: optional override of default expiry time.
# -----------------------------------------------------------------------------
def create_access_token(subject: str, role: str, expires_minutes: Optional[int] = None) -> str:
    # Use default expiry from settings if not provided
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    # Calculate expiry timestamp (UTC now + minutes)
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)

    # Payload of JWT:
    # - "sub" (subject): who the token is for (usually user ID/email).
    # - "role": embed role for role-based auth.
    # - "exp": expiration time (UTC timestamp).
    to_encode: dict[str, Any] = {"sub": subject, "role": role, "exp": expire}

    # Encode payload into a JWT string
    # - Uses HS256 (HMAC-SHA256) with our secret key.
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# -----------------------------------------------------------------------------
# 5) Decode and verify a JWT token
# -----------------------------------------------------------------------------
# - Input: encoded JWT string from client request.
# - Output: payload dict if valid, else raises ValueError.
def decode_token(token: str) -> dict[str, Any]:
    try:
        # Decode the token using same secret and algorithm.
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        # Any decoding/validation failure → raise ValueError for app to handle
        raise ValueError("Invalid token") from e
