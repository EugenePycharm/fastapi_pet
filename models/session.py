"""
Модель сессии (Session).

Хранит refresh токены и информацию о сессиях пользователей.
Используется для управления аутентификацией и JWT refresh flow.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, CreatedAt

if TYPE_CHECKING:
    from models.user import User


class Session(Base):
    """
    Модель пользовательской сессии.

    Хранит refresh токены и метаданные сессии для управления
    безопасностью и возможностью отзыва сессий.

    Атрибуты:
        id: UUID первичный ключ
        user_id: Foreign key на пользователя
        refresh_token: Хеш refresh токена (не хранить в plain text!)
        user_agent: User-Agent строка клиента
        ip_address: IP адрес клиента
        expires_at: Дата истечения сессии
        is_revoked: Флаг отзыва сессии
        created_at: Дата создания сессии

    Relationships:
        user: Пользователь, которому принадлежит сессия
    """

    __tablename__ = "sessions"

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя",
    )

    # Поля сессии
    refresh_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
        comment="Хеш refresh токена",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="User-Agent клиента",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP адрес клиента",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Дата истечения сессии",
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        index=True,
        comment="Флаг отзыва сессии",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
        lazy="joined",
    )

    # Индексы для частых запросов
    __table_args__ = (
        Index("ix_sessions_user_expires", "user_id", "expires_at"),
        Index("ix_sessions_active", "user_id", "is_revoked", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
