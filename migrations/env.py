from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.database import get_database_url
from app.models import Base


config = context.config

if config.config_file_name is not None:
    # `disable_existing_loggers` steht sonst auf True und schaltet **jeden**
    # bereits angelegten Logger ab — auch alle aus `app.`. In der Testsuite
    # läuft die Migration einmal vorweg; danach protokollierte die Anwendung
    # bis zum 20.08. still gar nichts mehr, und ein Test, der eine Logzeile
    # prüfen wollte, sah eine leere Liste.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
