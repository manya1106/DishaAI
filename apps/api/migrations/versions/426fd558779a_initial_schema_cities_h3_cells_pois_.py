"""initial schema: cities, h3_cells, pois, agent_runs

Revision ID: 426fd558779a
Revises:
Create Date: 2026-10-18 10:39:16.980896

Written by hand rather than trusting `alembic revision --autogenerate`:
autogenerate diffed against the postgis/postgis image's own TIGER
geocoder and topology extension tables (addr, edges, faces, state,
spatial_ref_sys, ...) and proposed dropping all of them. This
migration only ever creates our four application tables; PostGIS's
own extension tables are never touched.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = '426fd558779a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False, server_default='India'),
        sa.Column('bbox', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('h3_resolution', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'h3_cells',
        sa.Column('h3_index', sa.String(), primary_key=True),
        sa.Column('city_id', sa.Integer(), sa.ForeignKey('cities.id'), nullable=False),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('boundary', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('locality_name', sa.String(), nullable=True),
        sa.Column('rent_tier', sa.Integer(), nullable=True),
        sa.Column('ineligible', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('neighbourhood_pois', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    # Note: GeoAlchemy2's Geometry type auto-creates a GIST index on
    # `centroid` (named idx_h3_cells_centroid) via DDL events, so no
    # explicit op.create_index for it here.
    op.create_index('idx_h3_cells_city_id', 'h3_cells', ['city_id'])

    op.create_table(
        'pois',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('osm_type', sa.String(), nullable=False),
        sa.Column('osm_id', sa.BigInteger(), nullable=False),
        sa.Column('h3_index', sa.String(), sa.ForeignKey('h3_cells.h3_index'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('group_tag', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('geom', Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.UniqueConstraint('osm_type', 'osm_id', name='uq_pois_osm_type_id'),
    )
    # Same here: GeoAlchemy2 auto-creates idx_pois_geom for the
    # geometry column.
    op.create_index('idx_pois_h3_index', 'pois', ['h3_index'])
    op.create_index('idx_pois_category', 'pois', ['category'])

    op.create_table(
        'agent_runs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('trace_id', sa.String(), nullable=False),
        sa.Column('step', sa.Integer(), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('recipient', sa.String(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_agent_runs_trace_id', 'agent_runs', ['trace_id'])


def downgrade() -> None:
    op.drop_table('agent_runs')
    op.drop_table('pois')
    op.drop_table('h3_cells')
    op.drop_table('cities')
