# Enable forward references in type hints (helps when classes refer to
# each other before they’re defined). Not strictly needed here, but common.
from __future__ import annotations

# asyncio is Python’s async framework. Alembic in async mode requires it
# to run migration commands inside an event loop.
import asyncio

# Used to configure logging from alembic.ini (so Alembic can log SQL, etc.)
from logging.config import fileConfig

# Alembic supports async engines. This helper builds an async SQLAlchemy engine
# from the config options in alembic.ini.
from sqlalchemy.ext.asyncio import async_engine_from_config

# NullPool disables connection pooling (each connection is new and disposed).
# This is recommended for migrations to avoid connection conflicts.
from sqlalchemy.pool import NullPool

# Alembic’s main API for context during migration (offline/online modes, etc.)
from alembic import context


# Import project settings (DATABASE_URL is read here)
from app.core.settings import settings

# Import the shared Base class (Declarative Base for all models).
# Base.metadata tells Alembic what tables exist.
from app.core.database import Base

# Import all models so that they are attached to Base.metadata.
# Without this, Alembic’s autogenerate would see no models.
from app.models import base  # this line ensures User and future models are loaded


# ---------------------------------------------------------
# Alembic Config setup
# ---------------------------------------------------------

# Alembic config object, automatically populated from alembic.ini
config = context.config

# Load logging configuration from alembic.ini (so INFO/DEBUG logs work).
fileConfig(config.config_file_name)

# Target metadata = all tables from our SQLAlchemy models.
# Alembic uses this to compare models ↔ DB schema when autogenerating migrations.
target_metadata = Base.metadata

# Inject our DATABASE_URL (from settings.py / .env) into Alembic config.
# This overrides alembic.ini’s sqlalchemy.url with our dynamic environment value.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# ---------------------------------------------------------
# Migration functions
# ---------------------------------------------------------

# This function defines how migrations should run with a live DB connection.
# It configures Alembic with the connection + metadata and then runs migrations.
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,       # detect column type changes (not just adds/drops)
        render_as_batch=True,    # batch mode: useful for SQLite, safe for others too
    )
    # Open a transaction so all migration steps run atomically.
    with context.begin_transaction():
        context.run_migrations()


# Async version of migration runner (for asyncpg, etc.)
async def run_migrations_online():
    # Build an async engine using settings from alembic.ini (and overridden URL).
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",   # Alembic looks for keys like sqlalchemy.url
        poolclass=NullPool,     # no connection pooling during migrations
        future=True,            # use SQLAlchemy 2.0 style
    )

    # Open async connection
    async with connectable.connect() as connection:
        # Run migrations inside the connection context
        await connection.run_sync(do_run_migrations)

    # Dispose the engine cleanly
    await connectable.dispose()


# ---------------------------------------------------------
# Entrypoint: run migrations in the correct mode
# ---------------------------------------------------------

# Alembic supports two modes:
# - offline: generates SQL without touching DB
# - online: applies migrations against DB
#
# We only support online mode in this project (async DB).
if context.is_offline_mode():
    # Fail fast if someone tries `alembic upgrade --sql`
    raise Exception("This project only supports async (online) migrations.")
else:
    # Run migrations in async online mode
    asyncio.run(run_migrations_online())
