# Import the async engine creator and async session factory from SQLAlchemy
# - create_async_engine: builds an engine that talks to the database asynchronously
# - async_sessionmaker: factory to create sessions bound to that engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Import declarative_base, a helper for defining ORM models (tables)
# - Every model will subclass this "Base" so Alembic and SQLAlchemy know what tables exist
from sqlalchemy.orm import declarative_base

# Import project settings (contains DATABASE_URL from .env)
# - This allows the database URL to be configurable via environment variables
from app.core.settings import settings


# -----------------------------------------------------------------------------
# 1) Create SQLAlchemy async engine using DATABASE_URL
# -----------------------------------------------------------------------------
# - The engine manages the DB connection pool and is the "gateway" to Postgres.
# - We pass in settings.DATABASE_URL, which should look like:
#   postgresql+asyncpg://<username>:<password>@<host>:<port>/<dbname>
# - echo=True will log all SQL statements executed (good for debugging, noisy in production).
engine = create_async_engine(settings.DATABASE_URL, echo=True)


# -----------------------------------------------------------------------------
# 2) Create async session factory
# -----------------------------------------------------------------------------
# - A "Session" is the main entry point for talking to the database:
#   querying, adding, updating, deleting rows, etc.
# - async_sessionmaker creates a factory (AsyncSessionLocal) that produces
#   AsyncSession objects bound to our engine.
# - expire_on_commit=False means objects stay usable after commit,
#   instead of being expired and re-fetched on next access.
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False  # Don't expire ORM objects after commit
)


# -----------------------------------------------------------------------------
# 3) Declare base class for models
# -----------------------------------------------------------------------------
# - Every model (like User, Post, Comment) will inherit from Base.
# - This "Base" class stores metadata about all models, which Alembic uses
#   to autogenerate migrations (by comparing Base.metadata to the database schema).
Base = declarative_base()


# -----------------------------------------------------------------------------
# 4) Dependency for getting a database session in FastAPI routes
# -----------------------------------------------------------------------------
# - FastAPI can use "dependency injection" via `Depends(get_db)` in routes.
# - This function creates an AsyncSession for the duration of a request
#   and then ensures it's closed afterwards.
# - `yield` makes it a context-managed generator: FastAPI handles opening/closing.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------------------------------------------------------
# 5) Compatibility alias (get_session)
# -----------------------------------------------------------------------------
# - Some parts of the code may import get_session (old name).
# - By aliasing get_session = get_db, both names work and you don't break existing code.
get_session = get_db
