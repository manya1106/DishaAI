"""initial postgis schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-18 10:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 0. Ensure PostGIS extension is enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 1. cities table
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('boundary', Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_cities_slug', 'cities', ['slug'])

    # 2. h3_cells table
    op.create_table(
        'h3_cells',
        sa.Column('h3_index', sa.String(length=20), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('boundary', Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('locality_name', sa.Text(), nullable=True),
        sa.Column('rent_tier', sa.Integer(), nullable=True),
        sa.Column('ineligible', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('features', JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('h3_index')
    )
    op.create_index('idx_h3_cells_city_id', 'h3_cells', ['city_id'])

    # 3. pois table
    op.create_table(
        'pois',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('osm_type', sa.String(length=20), nullable=True),
        sa.Column('osm_id', sa.BigInteger(), nullable=True),
        sa.Column('h3_index', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('tags', JSONB(), nullable=True),
        sa.Column('geom', Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['h3_index'], ['h3_cells.h3_index'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('osm_type', 'osm_id', name='uq_pois_osm_natural_key')
    )
    op.create_index('idx_pois_h3_category', 'pois', ['h3_index', 'category'])

    # 4. cell_signals table
    op.create_table(
        'cell_signals',
        sa.Column('h3_index', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('budget_tier', sa.String(length=50), nullable=False),
        sa.Column('signal_name', sa.String(length=100), nullable=False),
        sa.Column('raw_value', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('percentile', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('provenance', sa.String(length=50), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['h3_index'], ['h3_cells.h3_index'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('h3_index', 'category', 'budget_tier', 'signal_name')
    )
    op.create_index('idx_cell_signals_lookup', 'cell_signals', ['h3_index', 'category', 'budget_tier'])

    # 5. agent_runs table
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('trace_id', sa.String(length=64), nullable=False),
        sa.Column('step', sa.Integer(), nullable=False),
        sa.Column('sender', sa.String(length=50), nullable=False),
        sa.Column('recipient', sa.String(length=50), nullable=False),
        sa.Column('payload', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_runs_trace_step', 'agent_runs', ['trace_id', 'step'])


def downgrade() -> None:
    op.drop_table('agent_runs')
    op.drop_table('cell_signals')
    op.drop_table('pois')
    op.drop_table('h3_cells')
    op.drop_table('cities')
