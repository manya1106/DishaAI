from datetime import UTC, datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    boundary = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    h3_cells: Mapped[list["H3Cell"]] = relationship("H3Cell", back_populates="city", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<City(slug='{self.slug}', name='{self.name}')>"


class H3Cell(Base):
    __tablename__ = "h3_cells"

    h3_index: Mapped[str] = mapped_column(String(20), primary_key=True)
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    centroid = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    boundary = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
    locality_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    rent_tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ineligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    features: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    city: Mapped["City"] = relationship("City", back_populates="h3_cells")
    pois: Mapped[list["POI"]] = relationship("POI", back_populates="h3_cell", cascade="all, delete-orphan")
    signals: Mapped[list["CellSignal"]] = relationship("CellSignal", back_populates="h3_cell", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<H3Cell(index='{self.h3_index}', locality='{self.locality_name}')>"


class POI(Base):
    __tablename__ = "pois"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    osm_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    h3_index: Mapped[str] = mapped_column(String(20), ForeignKey("h3_cells.h3_index", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    geom = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    h3_cell: Mapped["H3Cell"] = relationship("H3Cell", back_populates="pois")

    __table_args__ = (
        Index("idx_pois_h3_category", "h3_index", "category"),
        # Unique constraint on OSM ID when available
        UniqueConstraint("osm_type", "osm_id", name="uq_pois_osm_natural_key"),
    )

    def __repr__(self) -> str:
        return f"<POI(id={self.id}, name='{self.name}', category='{self.category}')>"


class CellSignal(Base):
    __tablename__ = "cell_signals"

    h3_index: Mapped[str] = mapped_column(String(20), ForeignKey("h3_cells.h3_index", ondelete="CASCADE"), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), primary_key=True)
    budget_tier: Mapped[str] = mapped_column(String(50), primary_key=True)
    signal_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    raw_value: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    percentile: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    provenance: Mapped[str] = mapped_column(String(50), nullable=False)  # 'measured' | 'estimated' | 'heuristic' | 'unavailable'
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    h3_cell: Mapped["H3Cell"] = relationship("H3Cell", back_populates="signals")

    __table_args__ = (
        Index("idx_cell_signals_lookup", "h3_index", "category", "budget_tier"),
    )

    def __repr__(self) -> str:
        return f"<CellSignal(cell='{self.h3_index}', signal='{self.signal_name}', p={self.percentile})>"


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    sender: Mapped[str] = mapped_column(String(50), nullable=False)
    recipient: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_agent_runs_trace_step", "trace_id", "step"),
    )

    def __repr__(self) -> str:
        return f"<AgentRun(trace_id='{self.trace_id}', step={self.step}, sender='{self.sender}')>"
