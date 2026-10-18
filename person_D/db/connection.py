import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Load environment from person_D/.env or repo root .env
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

DEFAULT_DB_URL = "postgresql+asyncpg://disha_user:disha_password@localhost:5432/disha"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Ensure asyncpg driver dialect is used if plain postgresql:// is provided
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

from sqlalchemy.pool import NullPool

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            poolclass=NullPool,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _sessionmaker


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    maker = get_sessionmaker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_health() -> dict[str, str | bool | float]:
    start_time = time.time()
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            # Check basic query and postgis extension
            result = await conn.execute(text("SELECT PostGIS_Version();"))
            version_row = result.fetchone()
            postgis_version = str(version_row[0]) if version_row else "unknown"
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "healthy",
                "connected": True,
                "postgis_version": postgis_version,
                "latency_ms": latency_ms,
            }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(exc),
            "latency_ms": round((time.time() - start_time) * 1000, 2),
        }
