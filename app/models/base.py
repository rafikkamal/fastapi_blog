from app.core.database import Base

# This file will later import all models
# so that Alembic can detect them for migrations

from app.models.user import User  # For user
