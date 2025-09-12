# Enable forward references in type hints.
# Example: if class A refers to class B before B is defined, it still works.
from __future__ import annotations

# Import specific column/data types from SQLAlchemy.
# - Boolean → true/false values
# - DateTime → timestamp columns
# - Enum → database enum type
# - Integer → integer numbers (used for primary keys, etc.)
# - String → variable-length string columns
from sqlalchemy import Boolean, DateTime, Enum, Integer, String

# Import SQLAlchemy’s ORM tools for type-annotated models:
# - Mapped → used for type hints (e.g., id: Mapped[int])
# - mapped_column → defines how each Python attribute maps to a DB column
from sqlalchemy.orm import Mapped, mapped_column

# Import the base class for our models.
# This Base comes from app/core/database.py (Declarative Base).
from app.core.database import Base

# Python’s built-in enum library lets us define fixed sets of values.
import enum

# datetime.utcnow is used as the default for created_at and updated_at.
from datetime import datetime


# ------------------------
# ENUM: UserRole
# ------------------------
# Define possible user roles in the system.
# This will be stored as a PostgreSQL enum type (super_admin, editor, subscriber).
class UserRole(str, enum.Enum):
    # Each role is a string value (str subclass ensures nice str behavior in DB).
    SUPER_ADMIN = "super_admin"
    EDITOR = "editor"
    SUBSCRIBER = "subscriber"


# ------------------------
# TABLE: users
# ------------------------
# Define the "users" table in the database by creating a model class.
# Every attribute here corresponds to a database column.
class User(Base):
    __tablename__ = "users"  # The actual table name in Postgres

    # Primary key (unique id for each user)
    id: Mapped[int] = mapped_column(
        Integer,                # column type: integer
        primary_key=True,       # marks as primary key
        index=True              # add index for faster lookups
    )

    # User’s email (must be unique, cannot be null)
    email: Mapped[str] = mapped_column(
        String,                 # column type: variable-length string
        unique=True,            # no two users can have the same email
        nullable=False,         # cannot be null
        index=True              # index for quick searches
    )

    # Full name of the user (optional, can be null)
    full_name: Mapped[str] = mapped_column(
        String,
        nullable=True
    )

    # Whether the account is active (default True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    # Role of the user (Super Admin, Editor, Subscriber).
    # Stored as an Enum in the DB.
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"),  # "userrole" is the name of the DB enum type
        nullable=False,                   # must always have a role
        default=UserRole.SUBSCRIBER       # default role is subscriber
    )

    # Password hash (hashed password, never store plain text passwords!)
    password_hash: Mapped[str] = mapped_column(
        String(255),           # up to 255 characters
        nullable=False         # password must always be set
    )

    # Timestamp when the user was created (defaults to current UTC time)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Timestamp when the user was last updated.
    # Automatically updated whenever the row changes.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
