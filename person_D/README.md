# person_D — PostgreSQL + PostGIS Data Layer & Scoring Agent

This directory contains the complete data foundation (Phase D) and Scoring Agent wrapper (Phase 2) for Disha AI, built in compliance with `plan.md` and `progress.md`.

---

## 1. Directory Structure

```
person_D/
├── docker-compose.yml       # PostGIS 16-3.4 local container configuration
├── .env.example             # Database credentials template
├── .env                     # Local credentials (git-ignored)
├── requirements.txt         # SQLAlchemy, Alembic, asyncpg, psycopg, geoalchemy2, shapely
├── alembic.ini              # Alembic migration configuration
├── alembic/
│   ├── env.py               # Async/Sync migration runner targeting Base.metadata
│   └── versions/
│       └── 001_initial_postgis_schema.py   # DDL for cities, h3_cells, pois, cell_signals, agent_runs
├── db/
│   ├── __init__.py          # Exports Base, models, and session utilities
│   ├── connection.py        # Async engine, sessionmaker, health checker
│   └── models.py            # SQLAlchemy 2.0 Declarative models with GeoAlchemy2 geometries
├── loader.py                # DatabaseLoader reading from PostGIS with snapshot fallback
├── scoring_agent.py         # Autonomous Scoring Agent wrapper (Phase 2)
├── scripts/
│   ├── load_snapshot_to_db.py   # Idempotent loader migrating blr.json into PostGIS
│   └── verify_db.py         # Diagnostic verifying PostGIS extension, health, & table counts
└── tests/
    ├── test_db_idempotency.py      # Asserts loader idempotency (Gate D.7)
    ├── test_db_scoring_parity.py   # Asserts bit-for-bit parity with snapshot (Gate D.9)
    └── test_scoring_agent.py       # Asserts ScoringAgent golden test parity (Gate 2.1.2)
```

---

## 2. Quickstart & Verification Commands

### Start Database
```bash
cd person_D && docker compose up -d
```

### Apply Migrations
```bash
cd person_D && alembic upgrade head
```

### Load Snapshot Data (417 H3 Res-8 cells, 2,592 POIs)
```bash
python person_D/scripts/load_snapshot_to_db.py
```

### Verify PostGIS Health & Integrity
```bash
python person_D/scripts/verify_db.py
```

### Run All Person D Tests
```bash
PYTHONPATH=. pytest person_D/tests/ -v
```
