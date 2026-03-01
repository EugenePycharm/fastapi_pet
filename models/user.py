"""
Модель пользователя (User).

Хранит данные аутентификации и профиль пользователя.
Пароль хранится в хешированном виде (bcrypt/argon2).
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, CreatedAt, UpdatedAt

if TYPE_CHECKING:
    from models.chat import Chat
    from models.session import Session
    from models.user_settings import UserSettings


class User(Base):
    """
    Модель пользователя для системы аутентификации.

    Атрибуты:
        id: UUID первичный ключ
        email: Уникальный email (lowercase)
        hashed_password: Хеш пароля (bcrypt/argon2)
        is_active: Статус активности (для soft delete)
        is_superuser: Флаг администратора
        created_at: Дата создания (timezone-aware)
        updated_at: Дата последнего обновления (timezone-aware)

    Relationships:
        sessions: Список сессий пользователя
        chats: Список чатов пользователя
    """

    __tablename__ = "users"

    # Поля
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальный email пользователя",
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Хеш пароля",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        index=True,
        comment="Статус активности пользователя",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        comment="Флаг администратора",
    )

    # Relationships с каскадным удалением
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    chats: Mapped[list["Chat"]] = relationship(
        "Chat",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Индексы для частых запросов
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
