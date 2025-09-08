import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.pool import NullPool
from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models import base  # import all models so Alembic sees them

# Alembic Config object
config = context.config

# Load logging config from alembic.ini
fileConfig(config.config_file_name)

# Set your target metadata for 'autogenerate'
target_metadata = Base.metadata

# Inject dynamic DB URL into Alembic config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # detect column type changes
        render_as_batch=True,  # useful for SQLite (optional)
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    # Create async engine
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# ✅ THIS IS CRUCIAL: run the coroutine properly
if context.is_offline_mode():
    raise Exception("This project only supports async (online) migrations.")
else:
    asyncio.run(run_migrations_online())
