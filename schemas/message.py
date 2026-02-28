"""
Pydantic схемы для модели Message.
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """Роль отправителя сообщения."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """Базовая схема сообщения."""

    model_config = ConfigDict(from_attributes=True)

    role: str = Field(
        ...,
        description="Роль отправителя",
        examples=["user"],
        pattern="^(user|assistant|system)$",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Текст сообщения",
        examples=["Привет! Как дела?"],
    )
    token_count: int | None = Field(
        None,
        description="Количество токенов",
        ge=0,
    )


class MessageCreate(MessageBase):
    """Схема для создания сообщения."""

    pass


class Message(MessageBase):
    """Полная схема сообщения."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID сообщения")
    chat_id: uuid.UUID = Field(..., description="ID чата")
    created_at: datetime = Field(..., description="Дата создания")
