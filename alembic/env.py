import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

from app.models.user_model import Base  # Import the declarative base to expose metadata

# ------------------------------------------------------------------------
# Load environment variables from .env file
# This allows dynamic configuration such as database URL for local/dev/prod
# ------------------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------------------
# Alembic Config object, provides access to the .ini configuration file.
# Used to configure logging and get database connection info.
# ------------------------------------------------------------------------
config = context.config

# ------------------------------------------------------------------------
# Inject the DATABASE_URL from environment variables into Alembic config.
# This overrides the 'sqlalchemy.url' key in alembic.ini
# Useful for running migrations across environments with .env configuration
# ------------------------------------------------------------------------
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# ------------------------------------------------------------------------
# Set up loggers defined in alembic.ini (if present)
# This helps in debugging migration commands
# ------------------------------------------------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------------------
# Target metadata — required for 'autogenerate' support.
# Alembic uses this to compare your models against the database schema
# and generate migration scripts automatically.
# ------------------------------------------------------------------------
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Runs migrations in 'offline' mode.

    This is useful for generating SQL migration scripts
    without connecting to a live database.

    - Uses the DATABASE_URL from config (injected from env)
    - Uses literal_binds=True to embed actual values into the SQL
    - Output is pure SQL text, not applied to any database
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # Ensures parameters are rendered as literal values
        dialect_opts={"paramstyle": "named"},  # Use named parameter syntax (:name)
    )

    # Begin migration transaction and emit SQL statements
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Runs migrations in 'online' mode.

    This directly connects to the database and applies migration scripts.

    - Uses SQLAlchemy's engine_from_config() to create a connection
    - Provides the connection and model metadata to Alembic
    - Runs the actual migrations within a DB transaction
    """
    # Create database engine using settings from alembic config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",  # Prefix in alembic.ini like sqlalchemy.url, etc.
        poolclass=pool.NullPool,  # Do not reuse connections across threads/processes
    )

    # Establish a live connection and apply migrations
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        # Run migrations inside a transaction block
        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------------------
# Choose mode based on CLI context
# Offline: emits SQL statements to a script
# Online: applies SQL directly to a live database
# ------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()