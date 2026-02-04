from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

# Try to load .env files for local development (optional)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Try loading from various locations for local dev
    current_dir = Path(__file__).resolve().parent
    load_dotenv(current_dir / ".env")  # apps/api/.env
    load_dotenv(current_dir / "dev.env")  # apps/api/dev.env
    
    # Try parent directories for monorepo structure
    for parent in current_dir.parents:
        env_file = parent / "dev.env"
        if env_file.exists():
            load_dotenv(env_file)
            break
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

# Use SQLite for dev, allow override for Postgres in production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./params.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Enable for debugging
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
