from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for dev, allow override for Postgres
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
