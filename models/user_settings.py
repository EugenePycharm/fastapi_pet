"""
Модель настроек пользователя (UserSettings).

Хранит пользовательские настройки:
- API ключ Google для доступа к Gemini
- Предпочитаемая модель
- Другие настройки
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, CreatedAt, UpdatedAt

if TYPE_CHECKING:
    from models.user import User


class UserSettings(Base):
    """
    Модель настроек пользователя.

    Атрибуты:
        id: UUID первичный ключ
        user_id: Foreign key на пользователя (уникальный)
        api_key: API ключ Google (опционально, если не задан используется серверный)
        model: Предпочитаемая модель Gemini
        created_at: Дата создания
        updated_at: Дата последнего обновления

    Relationships:
        user: Пользователь, которому принадлежат настройки
    """

    __tablename__ = "user_settings"

    # Доступные модели Gemini
    AVAILABLE_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-3-flash-preview",
    ]

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="ID пользователя",
    )

    # Поля настроек
    api_key: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Персональный API ключ Google",
    )
    model: Mapped[str] = mapped_column(
        String(100),
        default="gemini-2.5-flash-lite",
        nullable=False,
        comment="Предпочитаемая модель Gemini",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings",
        lazy="joined",
    )

    # Индексы
    __table_args__ = (
        Index("ix_user_settings_user_id", "user_id"),
        Index("ix_user_settings_model", "model"),
    )

    def __repr__(self) -> str:
        return f"<UserSettings(user_id={self.user_id}, model={self.model})>"
