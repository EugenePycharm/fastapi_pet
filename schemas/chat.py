"""
Pydantic схемы для модели Chat.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.message import Message


class ChatBase(BaseModel):
    """Базовая схема чата."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название чата",
        examples=["Мой первый чат"],
    )


class ChatCreate(ChatBase):
    """Схема для создания чата."""

    pass


class ChatUpdate(BaseModel):
    """Схема для обновления чата."""

    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Новое название чата",
    )


class Chat(ChatBase):
    """Полная схема чата."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID чата")
    user_id: uuid.UUID = Field(..., description="ID владельца")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class ChatWithMessages(Chat):
    """Схема чата с сообщениями."""

    messages: list[Message] = Field(
        default_factory=list,
        description="Сообщения в чате",
    )
