"""
Сервис для работы с Google Gemini API.

Поддерживает:
- Потоковую передачу ответов (streaming)
- Управление историей чата
- Контекст диалога
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from google import genai
from google.genai import types

from config import config_env


class GeminiService:
    """Сервис для взаимодействия с Google Gemini."""

    def __init__(self, model: str = "gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=config_env.API_KEY)
        self.model = model
        self._chat = None

    def _get_chat(self):
        """Получает или создаёт чат с Gemini."""
        if self._chat is None:
            self._chat = self.client.chats.create(
                model=self.model,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                ),
            )
        return self._chat

    async def stream_response(
        self,
        message: str,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Потоковая передача ответа от Gemini.

        Args:
            message: Сообщение пользователя
            system_prompt: Системный промпт (опционально)

        Yields:
            Части ответа (chunks)
        """
        chat = self._get_chat()

        # Добавляем system prompt если есть
        if system_prompt and not self._has_system_prompt(chat):
            chat.send_message(f"System instruction: {system_prompt}")

        # Потоковая передача ответа
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message_stream(message),
        )

        # Итерируем по частям
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def _has_system_prompt(self, chat) -> bool:
        """Проверяет, есть ли уже системный промпт в истории."""
        history = chat.get_history()
        if not history:
            return False
        # Проверяем первое сообщение
        first_message = history[0]
        if first_message.parts:
            text = first_message.parts[0].text or ""
            return text.startswith("System instruction:")
        return False

    def get_history(self) -> list[dict[str, str]]:
        """Получает историю чата."""
        chat = self._get_chat()
        history = chat.get_history()
        return [
            {"role": msg.role, "content": msg.parts[0].text if msg.parts else ""}
            for msg in history
        ]

    def clear_history(self) -> None:
        """Очищает историю чата."""
        self._chat = None


# Глобальный экземпляр сервиса
gemini_service = GeminiService()
