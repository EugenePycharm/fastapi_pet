"""
Сервис для работы с Google Gemini API.

Поддерживает:
- Потоковую передачу ответов (streaming)
- Управление историей чата
- Контекст диалога
- Пользовательские API ключи
- Выбор модели
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any, Optional

from google import genai
from google.genai import types

from config import config_env


class GeminiService:
    """Сервис для взаимодействия с Google Gemini."""

    DEFAULT_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-3-flash-preview",
    ]

    def __init__(self):
        self.default_api_key = config_env.API_KEY
        self.default_model = "gemini-2.5-flash-lite"

    def get_client(self, api_key: Optional[str] = None) -> genai.Client:
        """Получает клиент Gemini с указанным API ключом."""
        key = api_key or self.default_api_key
        return genai.Client(api_key=key)

    async def stream_response(
        self,
        message: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Потоковая передача ответа от Gemini.

        Args:
            message: Сообщение пользователя
            model: Модель Gemini (по умолчанию gemini-2.5-flash-lite)
            api_key: Персональный API ключ (опционально)
            system_prompt: Системный промпт (опционально)

        Yields:
            Части ответа (chunks) - по одному символу для плавного отображения
        """
        client = self.get_client(api_key)
        model_name = model or self.default_model

        # Создаём чат
        chat = client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )

        # Добавляем system prompt если есть
        if system_prompt:
            chat.send_message(f"System instruction: {system_prompt}")

        # Потоковая передача ответа
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message_stream(message),
        )

        # Собираем весь текст из streaming response
        full_text = ""
        for chunk in response:
            if chunk.text:
                full_text += chunk.text

        # Теперь отдаём посимвольно с правильной async задержкой
        for i, char in enumerate(full_text):
            yield char
            # Задержка каждые 3 символа для создания эффекта печати
            if i % 3 == 0:
                await asyncio.sleep(0.01)

    async def test_api_key(self, api_key: str) -> bool:
        """
        Тестирует API ключ на валидность.

        Returns:
            True если ключ действителен, False иначе
        """
        try:
            client = self.get_client(api_key)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.models.list(),
            )
            return True
        except Exception:
            return False


# Глобальный экземпляр сервиса
gemini_service = GeminiService()
