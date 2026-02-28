"""
Роутер для управления чатами.

Endpoints:
- GET /chats - список чатов пользователя
- POST /chats - создать чат
- GET /chats/{id} - получить чат с сообщениями
- DELETE /chats/{id} - удалить чат
- POST /chats/{id}/message - отправить сообщение (streaming)

Все endpoints требуют аутентификацию.
"""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from models.chat import Chat
from models.message import Message, MessageRole
from routers.auth import get_current_user
from schemas.chat import Chat as ChatSchema
from schemas.chat import ChatCreate, ChatWithMessages
from schemas.message import Message as MessageSchema
from schemas.message import MessageCreate
from services.gemini_service import gemini_service
from models.user import User

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("", response_model=list[ChatSchema])
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    limit: int = 20,
    offset: int = 0,
) -> list[Chat]:
    """Получить список чатов пользователя."""
    result = await db.execute(
        select(Chat)
        .where(Chat.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.post("", response_model=ChatSchema, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Chat:
    """Создать новый чат."""
    chat = Chat(
        user_id=current_user.id,
        title=chat_data.title,
    )

    db.add(chat)
    await db.flush()
    await db.refresh(chat)

    return chat


@router.get("/{chat_id}", response_model=ChatWithMessages)
async def get_chat(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Chat:
    """Получить чат с сообщениями."""
    result = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Удалить чат."""
    result = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    await db.delete(chat)


@router.post("/{chat_id}/message/stream")
async def send_message_stream(
    chat_id: uuid.UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Отправить сообщение и получить потоковый ответ от Gemini.

    Возвращает Server-Sent Events (SSE) поток.
    Требует аутентификацию.
    """
    # Проверяем существование чата и принадлежность пользователю
    result = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    # Конвертируем роль в enum (берём value из Enum)
    role_value = message_data.role.value if hasattr(message_data.role, 'value') else message_data.role
    role = MessageRole(role_value)

    # Сохраняем сообщение пользователя
    user_message = Message(
        chat_id=chat_id,
        role=role,
        content=message_data.content,
    )
    db.add(user_message)
    await db.flush()

    # Генерируем ответ
    async def generate_response():
        """Генератор SSE событий."""
        assistant_message = Message(
            chat_id=chat_id,
            role=MessageRole.ASSISTANT,
            content="",
        )
        db.add(assistant_message)

        full_response = ""

        try:
            async for chunk in gemini_service.stream_response(message_data.content):
                full_response += chunk
                # Формируем SSE событие
                event_data = {
                    "type": "chunk",
                    "content": chunk,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                yield f"data: {json.dumps(event_data)}\n\n"

            # Сохраняем полный ответ
            assistant_message.content = full_response
            await db.commit()

            # Финальное событие
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            # Событие ошибки
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            await db.rollback()

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Отключаем буферизацию nginx
        },
    )


@router.post("/{chat_id}/message", response_model=MessageSchema)
async def send_message(
    chat_id: uuid.UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Message:
    """
    Отправить сообщение и получить полный ответ от Gemini.

    Без потоковой передачи. Требует аутентификацию.
    """
    # Проверяем существование чата и принадлежность пользователю
    result = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    # Сохраняем сообщение пользователя
    user_message = Message(
        chat_id=chat_id,
        role=MessageRole.USER,
        content=message_data.content,
    )
    db.add(user_message)

    # Генерируем ответ
    full_response = ""
    async for chunk in gemini_service.stream_response(message_data.content):
        full_response += chunk

    # Сохраняем ответ ассистента
    assistant_message = Message(
        chat_id=chat_id,
        role=MessageRole.ASSISTANT,
        content=full_response,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return assistant_message
