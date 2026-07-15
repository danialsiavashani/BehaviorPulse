import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.base import Base
from app.db.models.user import User  # noqa: F401
from app.db.models.client_app import ClientApp  # noqa: F401
from app.db.models.api_key import ApiKey  # noqa: F401
from app.db.models.service import Service  # noqa: F401
from app.db.models.client_service_scope import ClientServiceScope  # noqa: F401
from app.db.models.request_log import ApiRequestLog  # noqa: F401
from app.db.models.observation_analysis import ObservationAnalysis  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.database_url)


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
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()