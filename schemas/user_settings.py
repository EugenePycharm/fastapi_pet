"""
Pydantic схемы для настроек пользователя.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSettingsBase(BaseModel):
    """Базовая схема настроек пользователя."""

    model_config = ConfigDict(from_attributes=True)

    model: str = Field(
        default="gemini-2.5-flash-lite",
        description="Модель Gemini для использования",
        examples=["gemini-2.5-flash-lite"],
    )


class UserSettingsCreate(UserSettingsBase):
    """Схема для создания настроек."""

    api_key: Optional[str] = Field(
        None,
        description="Персональный API ключ Google",
        examples=["AIzaSy..."],
    )


class UserSettingsUpdate(BaseModel):
    """Схема для обновления настроек."""

    model_config = ConfigDict(from_attributes=True)

    api_key: Optional[str] = Field(
        None,
        description="Персональный API ключ Google (оставьте пустым для использования серверного)",
    )
    model: Optional[str] = Field(
        None,
        description="Модель Gemini для использования",
    )


class UserSettings(UserSettingsBase):
    """Полная схема настроек пользователя."""

    model_config = ConfigDict(from_attributes=True, json_schema_extra={'api_key': None})

    id: uuid.UUID = Field(..., description="ID настроек")
    user_id: uuid.UUID = Field(..., description="ID пользователя")
    api_key: Optional[str] = Field(None, description="API ключ (скрыт)")
    has_api_key: bool = Field(..., description="Установлен ли персональный API ключ")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class UserSettingsList(BaseModel):
    """Схема списка настроек."""

    available_models: list[str] = Field(
        ...,
        description="Список доступных моделей",
    )
    settings: Optional[UserSettings] = Field(
        ...,
        description="Текущие настройки пользователя",
    )
