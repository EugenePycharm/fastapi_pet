"""
Роутер для аутентификации пользователей.

Endpoints:
- POST /auth/register - регистрация нового пользователя
- POST /auth/login - вход и получение токенов
- POST /auth/refresh - обновление access токена
- GET /auth/me - получение данных текущего пользователя
"""

import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from models.user import User
from schemas.auth import Token, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 схема для Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Получает текущего пользователя из JWT токена.

    Используется как dependency для защищённых endpoints.
    """
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или не активен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Регистрация нового пользователя.

    Создаёт нового пользователя с хешированным паролем.
    """
    # Проверяем существование пользователя с таким email
    result = await db.execute(
        select(User).where(User.email == user_data.email.lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    # Создаём нового пользователя
    user = User(
        email=user_data.email.lower(),
        hashed_password=get_password_hash(user_data.password),
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """
    Вход пользователя и получение токенов.

    Использует OAuth2 password flow для совместимости со Swagger UI.
    Отправьте email и password в форме.
    """
    # Ищем пользователя по email
    result = await db.execute(
        select(User).where(User.email == form_data.username.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован",
        )

    # Создаём токены
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15),  # Короткое время жизни
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/json", response_model=Token)
async def login_json(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """
    Вход пользователя через JSON body.

    Альтернатива OAuth2 форме для API клиентов.
    """
    # Ищем пользователя по email
    result = await db.execute(
        select(User).where(User.email == credentials.email.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован",
        )

    # Создаём токены
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15),
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: dict[str, str],
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """
    Обновление access токена через refresh токен.
    """
    refresh_token_str = token_data.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh токен не предоставлен",
        )

    user_id = verify_token(refresh_token_str)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем существование пользователя
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или не активен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаём новые токены
    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=15),
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Получение данных текущего пользователя.

    Требует валидный Bearer токен.
    """
    return current_user
