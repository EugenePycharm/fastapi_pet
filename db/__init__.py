"""
Пакет db - базовые компоненты для работы с базой данных.
"""

from db.base import Base, CreatedAt, UpdatedAt, UUID_PK

__all__ = [
    "Base",
    "CreatedAt",
    "UpdatedAt",
    "UUID_PK",
]
