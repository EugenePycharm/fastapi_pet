"""
Pydantic схемы для модели User.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль пользователя (минимум 8 символов)",
        examples=["SecurePassword123!"],
    )


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr | None = Field(
        None,
        description="Новый email",
        examples=["newemail@example.com"],
    )
    password: str | None = Field(
        None,
        min_length=8,
        max_length=100,
        description="Новый пароль",
    )
    is_active: bool | None = Field(
        None,
        description="Статус активности",
    )


class User(UserBase):
    """Полная схема пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID пользователя")
    is_active: bool = Field(..., description="Статус активности")
    is_superuser: bool = Field(..., description="Флаг администратора")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
