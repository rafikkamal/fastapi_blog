from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum

# Define possible user roles
class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    EDITOR = "editor"
    SUBSCRIBER = "subscriber"

# Define the user table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
