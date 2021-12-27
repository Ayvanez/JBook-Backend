import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

from app.core.config import get_app_settings  # isort:skip
from app.db.queries.tables import metadata

SETTINGS = get_app_settings()
DATABASE_ALEMBIC_URL = SETTINGS.database_alembic_url

config = context.config

fileConfig(config.config_file_name)  # type: ignore

target_metadata = metadata

config.set_main_option("sqlalchemy.url", str(DATABASE_ALEMBIC_URL))


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool

    )

    print(target_metadata.schema)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          include_schemas=True)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
