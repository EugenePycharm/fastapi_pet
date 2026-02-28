"""
Alembic env.py с поддержкой async SQLAlchemy 2.0.

Использует asyncpg для выполнения миграций в асинхронном режиме.
Поддерживает как online (прямое выполнение), так и offline (генерация SQL) режимы.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from core.config import settings
from db.base import Base
from models import *  # noqa: F401, F403 - импортируем все модели для Alembic

# Alembic Config object
config = context.config

# Переопределяем URL из настроек приложения (используем asyncpg)
config.set_main_option("sqlalchemy.url", settings.database_url)

# Target metadata для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Запуск миграций в offline режиме.

    Генерирует SQL скрипты без подключения к БД.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Запуск миграций в online режиме.

    Подключается к БД и выполняет миграции.
    Использует async engine для PostgreSQL.
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = asyncio.run(get_async_connection())

    if hasattr(connectable, "cursor"):
        # Синхронное подключение
        context.configure(
            connection=connectable,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    else:
        # Асинхронное подключение
        asyncio.run(run_async_migrations(connectable))


async def get_async_connection():
    """Создаёт async подключение для миграций."""
    engine = async_engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    return engine


async def run_async_migrations(engine):
    """Выполняет миграции в асинхронном режиме."""
    async with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
            dialect_opts={"paramstyle": "pyformat"},
        )

        async with connection.begin():
            # Используем правильный способ вызова для async
            await connection.run_sync(_run_migrations_sync)

    await engine.dispose()


def _run_migrations_sync(connection):
    """Синхронная функция для выполнения миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# Точка входа Alembic
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
