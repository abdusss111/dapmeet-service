import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# КРИТИЧЕСКИ ВАЖНО: Добавить путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Импортируем Base и ВСЕ модели для регистрации в MetaData
from dapmeet.db.db import Base

# ОБЯЗАТЕЛЬНО импортировать ВСЕ модели, иначе autogenerate их не увидит!
from dapmeet.models import user      # noqa: F401
from dapmeet.models import meeting   # noqa: F401  
from dapmeet.models import segment   # noqa: F401
from dapmeet.models import chat_message   # noqa: F401

# this is the MetaData object that Alembic uses for autogenerate
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """Получить URL базы данных из переменной окружения или конфига."""
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        # Используем переменную окружения как fallback
        url = os.getenv("DATABASE_URL", "postgresql://dapuser:dappass@db:5432/dapmeet")
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section, {})
    
    # Переопределяем URL если нужно
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Полезные опции для автогенерации
            render_as_batch=True,  # Для SQLite совместимости
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()