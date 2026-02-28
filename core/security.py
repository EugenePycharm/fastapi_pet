"""
Модуль безопасности: JWT токены и хеширование паролей.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from core.config import settings

# Алгоритм JWT
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хешу.

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хеш пароля

    Returns:
        True если пароль совпадает
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль.

    Args:
        password: Пароль в открытом виде

    Returns:
        Хеш пароля
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Создаёт JWT access токен.

    Args:
        data: Данные для кодирования (обычно {"sub": user_id})
        expires_delta: Время жизни токена

    Returns:
        JWT токен
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Создаёт JWT refresh токен.

    Args:
        data: Данные для кодирования
        expires_delta: Время жизни токена

    Returns:
        JWT токен
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return create_access_token(data, expires_delta=expires_delta)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Декодирует JWT токен.

    Args:
        token: JWT токен

    Returns:
        Данные токена или None если токен невалиден
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[str]:
    """
    Проверяет токен и возвращает user_id.

    Args:
        token: JWT токен

    Returns:
        user_id из токена или None если токен невалиден
    """
    payload = decode_token(token)
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    # Проверяем срок действия
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        return None

    return user_id
