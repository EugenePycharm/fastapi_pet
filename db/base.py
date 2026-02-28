"""
Базовые классы и утилиты для SQLAlchemy моделей.

Содержит:
- Базовый класс DeclarativeBase с UUID первичными ключами
- Mixin'ы для общих полей (created_at, updated_at)
- Типы данных для специфичных полей
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)


# Тип для UUID первичных ключей с автогенерацией
UUID_PK = Annotated[
    uuid.UUID,
    mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        index=True,
    ),
]

# Тип для timezone-aware datetime с автозаполнением
CreatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    ),
]

UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    ),
]


class Base(DeclarativeBase):
    """
    Базовый класс для всех ORM моделей.

    Особенности:
    - Автоматическое имя таблицы (множественное число класса)
    - Поддержка UUID первичных ключей
    - Индексы на первичных ключах
    """

    # Префикс для всех таблиц (опционально)
    __table_args__: dict[str, Any] = {"extend_existing": True}

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Генерирует имя таблицы во множественном числе."""
        class_name = cls.__name__
        # Простое правило: добавляем 's' если не заканчивается на 's'
        if class_name.endswith("s"):
            return class_name.lower()
        return f"{class_name.lower()}s"

    # Стандартные поля для всех моделей
    id: Mapped[UUID_PK]  # type: ignore[valid-type]
    created_at: Mapped[CreatedAt]  # type: ignore[valid-type]
    updated_at: Mapped[UpdatedAt]  # type: ignore[valid-type]

    def to_dict(self) -> dict[str, Any]:
        """Конвертирует модель в словарь (для сериализации)."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
