"""
Роутер для управления настройками пользователя.

Endpoints:
- GET /settings - получить настройки пользователя
- PUT /settings - обновить настройки
- POST /settings/test-api-key - протестировать API ключ
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from models.user import User
from models.user_settings import UserSettings
from routers.auth import get_current_user
from schemas.user_settings import (
    UserSettings as UserSettingsSchema,
)
from schemas.user_settings import (
    UserSettingsCreate,
    UserSettingsList,
    UserSettingsUpdate,
)

router = APIRouter(prefix="/settings", tags=["User Settings"])


@router.get("", response_model=UserSettingsList)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> UserSettingsList:
    """Получить настройки текущего пользователя."""
    # Получаем настройки пользователя
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()

    # Формируем ответ
    settings_data = None
    if user_settings:
        settings_data = UserSettingsSchema(
            id=user_settings.id,
            user_id=user_settings.user_id,
            api_key=None,  # Не возвращаем API ключ
            has_api_key=user_settings.api_key is not None,
            model=user_settings.model,
            created_at=user_settings.created_at,
            updated_at=user_settings.updated_at,
        )

    return UserSettingsList(
        available_models=UserSettings.AVAILABLE_MODELS,
        settings=settings_data,
    )


@router.put("", response_model=UserSettingsSchema)
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Обновить настройки текущего пользователя."""
    # Получаем или создаём настройки
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()

    if user_settings is None:
        # Создаём новые настройки
        user_settings = UserSettings(
            user_id=current_user.id,
            api_key=settings_data.api_key,
            model=settings_data.model or "gemini-2.5-flash-lite",
        )
        db.add(user_settings)
    else:
        # Обновляем существующие
        if settings_data.api_key is not None:
            user_settings.api_key = settings_data.api_key
        if settings_data.model is not None:
            user_settings.model = settings_data.model

    await db.commit()
    await db.refresh(user_settings)

    # Возвращаем данные в формате схемы
    return {
        "id": user_settings.id,
        "user_id": user_settings.user_id,
        "api_key": None,  # Не возвращаем API ключ
        "has_api_key": user_settings.api_key is not None,
        "model": user_settings.model,
        "created_at": user_settings.created_at,
        "updated_at": user_settings.updated_at,
    }


@router.post("/test-api-key")
async def test_api_key(
    api_key_data: dict[str, str],
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Протестировать API ключ Google.

    Отправляет простой запрос к Gemini API для проверки ключа.
    """
    import asyncio
    from google import genai
    from google.genai.errors import APIError

    api_key = api_key_data.get("api_key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API ключ не предоставлен",
        )

    try:
        # Создаём клиент с предоставленным ключом
        client = genai.Client(api_key=api_key)

        # Пробуем получить список моделей
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: client.models.list(),
        )

        return {
            "status": "success",
            "message": "API ключ действителен",
        }
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка API ключа: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при проверке ключа: {str(e)}",
        )
