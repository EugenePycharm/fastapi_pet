"""
FastAPI приложение с асинхронной поддержкой SQLAlchemy 2.0.

Включает:
- Lifespan events для инициализации/закрытия БД
- Dependency injection для сессий
- Health check endpoint
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import close_db, get_db_session, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan manager для инициализации и закрытия подключений к БД.

    Вызывается при старте и остановке приложения.
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="FastAPI Gemini Clone",
    description="Асинхронный API для чатов с AI ассистентом",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Проверка здоровья API",
    description="Возвращает статус работы приложения и подключения к БД.",
)
async def health_check() -> dict[str, str]:
    """Endpoint для проверки здоровья приложения."""
    return {
        "status": "healthy",
        "service": "fastapi-gemini-clone",
    }


@app.get(
    "/db/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Проверка подключения к БД",
    description="Проверяет доступность базы данных.",
)
async def db_health_check(db: Annotated[AsyncSession, Depends(get_db_session)]) -> dict[str, str]:
    """Endpoint для проверки подключения к базе данных."""
    from sqlalchemy import text

    await db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
    }


# =============================================================================
# Примечание: endpoints для пользователей, чатов и сообщений
# будут добавлены в отдельных роутерах (routers/)
# =============================================================================
