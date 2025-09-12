# Import the shared Declarative Base class that all models must inherit from.
# This Base was defined in app/core/database.py and is used to register tables.
from app.core.database import Base

# Import your models here so that they get registered on Base.metadata.
# If you don’t import them, Alembic’s `autogenerate` won’t know they exist,
# and migrations will not include their tables.
from app.models.user import User  # Import the User model so Alembic can see it

# In the future, you’ll add other models here as you create them:
# from app.models.post import Post
# from app.models.comment import Comment
#
# This ensures all tables are available in one place, linked to Base.metadata.
#
# Why is this needed?
# - Alembic doesn’t magically scan your whole project.
# - It only looks at `target_metadata = Base.metadata` in alembic/env.py.
# - So every model must be imported at least once so it gets attached to Base.metadata.
