"""
Модель чата (Chat).

Хранит информацию о чатах пользователей с AI ассистентом.
Каждый чат принадлежит одному пользователю и содержит сообщения.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, CreatedAt, UpdatedAt

if TYPE_CHECKING:
    from models.message import Message
    from models.user import User


class Chat(Base):
    """
    Модель чата пользователя.

    Представляет собой контейнер для сообщений между пользователем
    и AI ассистентом.

    Атрибуты:
        id: UUID первичный ключ
        user_id: Foreign key на владельца чата
        title: Название чата (генерируется автоматически или задаётся пользователем)
        created_at: Дата создания чата
        updated_at: Дата последнего сообщения в чате

    Relationships:
        user: Владелец чата
        messages: Список сообщений в чате (каскадное удаление)
    """

    __tablename__ = "chats"

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID владельца чата",
    )

    # Поля чата
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Новый чат",
        comment="Название чата",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="chats",
        lazy="joined",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Индексы для частых запросов
    __table_args__ = (
        Index("ix_chats_user_created", "user_id", "created_at"),
        Index("ix_chats_title", "title"),
    )

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, user_id={self.user_id}, title={self.title})>"
