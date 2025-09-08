from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create SQLAlchemy async engine using DATABASE_URL
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False  # Don't expire objects after commit
)

# Declare base class for models
Base = declarative_base()

# Dependency for getting a database session in FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
