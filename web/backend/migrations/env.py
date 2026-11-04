from logging.config import fileConfig

from alembic import context
from rendercv_web.db.models import Base
from rendercv_web.db.session import ensure_sqlite_directory, resolve_database_url
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# disable_existing_loggers=False keeps the host application's logging
# intact: the FastAPI lifespan runs this env.py at startup, and the
# default fileConfig behavior would silently strip uvicorn's handlers,
# swallowing every access line and error traceback after migration.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Why: migrations must run against the same database the app talks to
# (RENDERCV_WEB_DATABASE_URL), never a hardcoded URL baked into
# alembic.ini -- this overrides whatever `sqlalchemy.url` says there.
# `resolve_database_url` rather than a raw `os.environ` read: it is what
# rewrites a provider's `postgres://` / `postgresql://` string onto the
# driver actually installed. Reading the variable directly here is what
# made `alembic upgrade head` fail on a pasted connection string while
# the running app accepted it.
config.set_main_option("sqlalchemy.url", resolve_database_url())

# `target_metadata` enables `alembic revision --autogenerate` to diff the
# ORM models against the live schema; the models are the source of truth.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    ensure_sqlite_directory(url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=url.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = config.get_main_option("sqlalchemy.url")
    ensure_sqlite_directory(url)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=url.startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
