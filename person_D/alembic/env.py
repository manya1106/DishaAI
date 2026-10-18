import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Setup python path to include repo root and person_D
person_d_dir = Path(__file__).resolve().parents[1]
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Load env variables
env_file = person_d_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models metadata
from person_D.db.models import Base

target_metadata = Base.metadata

# Use SYNC_DATABASE_URL for Alembic migration commands
sync_db_url = os.getenv("SYNC_DATABASE_URL", "postgresql+psycopg://disha_user:disha_password@localhost:5432/disha")
config.set_main_option("sqlalchemy.url", sync_db_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
