"""
Асинхронная настройка SQLAlchemy 2.0 для PostgreSQL.

Использует asyncpg драйвер с оптимизированными настройками connection pool
для высокой производительности в production.
"""

from collections.abc import AsyncGenerator
from typing import Final

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from core.config import settings

# Настройки connection pool для production
# Оптимизировано для высокой нагрузки и асинхронной работы
POOL_SIZE: Final[int] = 10  # Количество постоянных соединений в пуле
MAX_OVERFLOW: Final[int] = 20  # Дополнительные соединения при пиковой нагрузке
POOL_TIMEOUT: Final[int] = 30  # Таймаут ожидания соединения (сек)
POOL_RECYCLE: Final[int] = 1800  # Пересоздание соединений через 30 минут
POOL_PRE_PING: Final[bool] = True  # Проверка соединения перед использованием

# Создание async engine
async_engine = create_async_engine(
    url=settings.database_url,
    echo=settings.DEBUG,  # Логирование SQL только в debug режиме
    poolclass=AsyncAdaptedQueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=POOL_PRE_PING,
    future=True,  # SQLAlchemy 2.0 стиль
)

# Factory для создания async сессий
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать объекты после commit
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI - предоставляет async сессию.

    Гарантирует закрытие сессии после использования.
    Автоматически откатывает незакоммиченные транзакции при ошибках.

    Usage:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализация соединений с БД (проверка доступности)."""
    from sqlalchemy import text

    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def close_db() -> None:
    """Закрытие всех соединений с БД при остановке приложения."""
    await async_engine.dispose()
