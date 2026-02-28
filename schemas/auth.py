"""
Pydantic схемы для аутентификации.
"""

import uuid

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Схема для регистрации пользователя."""

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль (минимум 8 символов)",
        examples=["SecurePassword123!"],
    )


class UserLogin(BaseModel):
    """Схема для входа пользователя."""

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="Пароль",
        examples=["SecurePassword123!"],
    )


class Token(BaseModel):
    """Схема ответа с токеном."""

    access_token: str = Field(..., description="JWT access токен")
    refresh_token: str = Field(..., description="JWT refresh токен")
    token_type: str = Field("bearer", description="Тип токена")


class TokenRefresh(BaseModel):
    """Схема для обновления токена."""

    refresh_token: str = Field(..., description="JWT refresh токен")


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""

    id: uuid.UUID
    email: EmailStr
    is_active: bool

    model_config = {"from_attributes": True}
