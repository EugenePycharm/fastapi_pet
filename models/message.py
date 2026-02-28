"""
Модель сообщения (Message).

Хранит сообщения в чатах между пользователем и AI ассистентом.
Поддерживает роли: user, assistant, system.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Index, Text, Uuid, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, CreatedAt

if TYPE_CHECKING:
    from models.chat import Chat


class MessageRole(str, Enum):
    """Роль отправителя сообщения."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    """
    Модель сообщения в чате.

    Хранит текст сообщения и метаданные для контекста диалога.

    Атрибуты:
        id: UUID первичный ключ
        chat_id: Foreign key на чат
        role: Роль отправителя (user/assistant/system)
        content: Текст сообщения
        token_count: Количество токенов (опционально, для статистики)
        created_at: Дата создания сообщения

    Relationships:
        chat: Чат, к которому принадлежит сообщение
    """

    __tablename__ = "messages"

    # Foreign Keys
    chat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
        index=True,
        comment="ID чата",
    )

    # Поля сообщения
    role: Mapped[MessageRole] = mapped_column(
        default=MessageRole.USER,
        nullable=False,
        index=True,
        comment="Роль отправителя",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст сообщения",
    )
    token_count: Mapped[Optional[int]] = mapped_column(
        default=None,
        nullable=True,
        comment="Количество токенов",
    )

    # Relationships
    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="messages",
        lazy="joined",
    )

    # Индексы для частых запросов
    __table_args__ = (
        Index("ix_messages_chat_created", "chat_id", "created_at"),
        Index("ix_messages_chat_role", "chat_id", "role"),
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, role={self.role.value})>"
