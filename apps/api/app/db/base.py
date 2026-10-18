"""Async SQLAlchemy engine/session setup for the Phase D data foundation.

See plan.md Phase D. Only used when settings.DATA_MODE == "postgres";
the JSON snapshot loader (apps/api/app/data/loader.py) remains the
default/fallback data source.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    if not settings.DATABASE_URL:
        return None
    return create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)


engine = _make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False) if engine else None


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured; cannot open a DB session")
    async with SessionLocal() as session:
        yield session
