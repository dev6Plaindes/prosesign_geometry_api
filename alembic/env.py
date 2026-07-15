import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Añadir el directorio src al path para poder importar modelos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar modelos
from src.bim.models.project_model import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url():
    """Build database URL from environment variables."""
    # Support both DB_PASSWORD (from GitHub Actions) and DB_PASS (legacy)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS", "root_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "db_arquitectura")

    # Validate required environment variables
    if not DB_USER:
        raise ValueError("DB_USER environment variable is required")
    if not DB_PASS:
        raise ValueError("DB_PASSWORD or DB_PASS environment variable is required")
    if not DB_HOST:
        raise ValueError("DB_HOST environment variable is required")
    if not DB_PORT:
        raise ValueError("DB_PORT environment variable is required")
    if not DB_NAME:
        raise ValueError("DB_NAME environment variable is required")

    try:
        DB_PORT_INT = int(DB_PORT)
    except ValueError:
        raise ValueError(f"DB_PORT must be a valid integer, got: '{DB_PORT}'")

    return f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT_INT}/{DB_NAME}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = get_database_url()
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()