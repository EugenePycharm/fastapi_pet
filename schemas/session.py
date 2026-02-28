"""
Pydantic схемы для модели Session.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionBase(BaseModel):
    """Базовая схема сессии."""

    model_config = ConfigDict(from_attributes=True)

    user_agent: str | None = Field(
        None,
        description="User-Agent клиента",
        examples=["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"],
    )
    ip_address: str | None = Field(
        None,
        description="IP адрес клиента",
        examples=["192.168.1.1"],
    )


class SessionCreate(SessionBase):
    """Схема для создания сессии."""

    refresh_token: str = Field(
        ...,
        description="Refresh токен",
    )
    expires_at: datetime = Field(
        ...,
        description="Дата истечения сессии",
    )


class Session(SessionBase):
    """Полная схема сессии."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID сессии")
    user_id: uuid.UUID = Field(..., description="ID пользователя")
    refresh_token: str = Field(..., description="Хеш refresh токена")
    expires_at: datetime = Field(..., description="Дата истечения")
    is_revoked: bool = Field(..., description="Флаг отзыва сессии")
    created_at: datetime = Field(..., description="Дата создания")
