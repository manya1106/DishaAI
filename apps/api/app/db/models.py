"""SQLAlchemy models for the Phase D data foundation.

Deviation from the originally drafted DDL (plan.md §6.1, approved as
drafted): the `cell_signals` table is replaced by a single JSONB
`features` column on `h3_cells`, matching the exact shape
`scoring/engine.py` already expects from the JSON snapshot
(`cell["features"][category]["competitor_density"]`, etc.). This makes
the Postgres-backed loader a drop-in replacement for the snapshot
loader with zero changes to the scoring engine. Logged in progress.md.

`centroid`/`geom` use PostGIS geometry types (per the owner's decision
to install PostGIS from the start); `boundary` stays JSONB, matching
the exact `list[list[float]]` polygon shape the frontend already
consumes via the API contract - no geometry operations are performed
on it today.
"""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False, default="India")
    bbox: Mapped[dict] = mapped_column(JSONB, nullable=False)
    h3_resolution: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cells: Mapped[list["H3Cell"]] = relationship(back_populates="city")


class H3Cell(Base):
    __tablename__ = "h3_cells"

    h3_index: Mapped[str] = mapped_column(String, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    centroid: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    boundary: Mapped[list] = mapped_column(JSONB, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    locality_name: Mapped[str | None] = mapped_column(String, nullable=True)
    rent_tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ineligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    neighbourhood_pois: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    city: Mapped["City"] = relationship(back_populates="cells")
    pois: Mapped[list["POI"]] = relationship(back_populates="cell")


class POI(Base):
    __tablename__ = "pois"
    __table_args__ = (UniqueConstraint("osm_type", "osm_id", name="uq_pois_osm_type_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    osm_type: Mapped[str] = mapped_column(String, nullable=False)
    osm_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    h3_index: Mapped[str] = mapped_column(ForeignKey("h3_cells.h3_index"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    group_tag: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    cell: Mapped["H3Cell"] = relationship(back_populates="pois")


class AgentRun(Base):
    """Optional Postgres-backed agent trace log (plan.md §6.1).

    Not wired up yet - Person M's in-memory TraceStore
    (apps/api/app/agents/contracts.py) remains the active
    implementation. This table exists so that swap can happen later
    without a schema change, per plan.md's "keep as fallback" decision.
    """

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trace_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    sender: Mapped[str] = mapped_column(String, nullable=False)
    recipient: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
