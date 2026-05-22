"""OpenRouter API integration with response caching."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from typing import TYPE_CHECKING, Any

import requests
from requests.exceptions import RequestException, Timeout

from ai.response_parser import AIResponseParser
from config import (
    FLASHCARD_COUNT,
    MAX_AI_INPUT_CHARS,
    MAX_CHUNK_CHARS,
    OPENROUTER_API_KEY,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_MODEL,
    QUIZ_QUESTION_COUNT,
)
from models.material import Material

if TYPE_CHECKING:
    from storage.json_storage import JSONStorage

logger = logging.getLogger(__name__)

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
REQUEST_TIMEOUT_SECONDS = 120

STUDY_PROMPT_TEMPLATE = """JSON only. Create study material from the text below.

Output schema:
{{"summary":"brief overview (max 400 chars)","flashcards":[{{"question":"...","answer":"..."}}],"quiz":[{{"question":"...","options":["A","B","C","D"],"correct_index":0}}]}}

Rules:
- Exactly {flashcard_count} flashcards and {quiz_count} quiz questions
- Keep answers under 80 chars; quiz options under 40 chars each
- No markdown, no extra keys, no commentary

Text:
{text}"""


class AIServiceError(Exception):
    """raised when API fail"""
class AIService:

    def __init__(
        self,
        api_key: str = OPENROUTER_API_KEY,
        model_name: str = OPENROUTER_MODEL,
        storage: JSONStorage | None = None,
    ) -> None:
        if not api_key:
            raise AIServiceError("OPENROUTER_API_KEY is not configured.")
        self._api_key = api_key
        self._model_name = model_name
        self.storage = storage
        self._parser = AIResponseParser()

    @staticmethod
    def cache_key(text: str) -> str:
        normalized = text.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def split_paragraph_chunks(text: str, max_chunk_chars: int = MAX_CHUNK_CHARS) -> list[str]:
        stripped = text.strip()
        if not stripped:
            return []

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", stripped) if p.strip()]
        if not paragraphs:
            paragraphs = [line.strip() for line in stripped.splitlines() if line.strip()]
        if not paragraphs:
            return [stripped[:max_chunk_chars]]

        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        def flush() -> None:
            nonlocal current, current_len
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0

        for para in paragraphs:
            if len(para) > max_chunk_chars:
                flush()
                for i in range(0, len(para), max_chunk_chars):
                    chunks.append(para[i : i + max_chunk_chars])
                continue

            extra = len(para) + (2 if current else 0)
            if current and current_len + extra > max_chunk_chars:
                flush()
            current.append(para)
            current_len += extra

        flush()
        return chunks

    @classmethod
    def prepare_input_text(
        cls,
        text: str,
        max_total_chars: int = MAX_AI_INPUT_CHARS,
        max_chunk_chars: int = MAX_CHUNK_CHARS,
    ) -> str:
        chunks = cls.split_paragraph_chunks(text, max_chunk_chars=max_chunk_chars)
        if not chunks:
            return ""

        selected: list[str] = []
        total = 0
        for chunk in chunks:
            extra = len(chunk) + (2 if selected else 0)
            if selected and total + extra > max_total_chars:
                break
            if not selected and len(chunk) > max_total_chars:
                selected.append(chunk[:max_total_chars])
                break
            selected.append(chunk)
            total += extra

        prepared = "\n\n".join(selected)
        if len(chunks) > len(selected):
            logger.info(
                "Input truncated: using %s/%s paragraph chunks (%s chars).",
                len(selected),
                len(chunks),
                len(prepared),
            )
        return prepared

    def _build_prompt(self, text: str) -> str:
        prepared = self.prepare_input_text(text)
        return STUDY_PROMPT_TEMPLATE.format(
            flashcard_count=FLASHCARD_COUNT,
            quiz_count=QUIZ_QUESTION_COUNT,
            text=prepared,
        )

    @staticmethod
    def _extract_error_detail(response: requests.Response) -> str:
        try:
            body = response.json()
            if isinstance(body, dict):
                error = body.get("error")
                if isinstance(error, dict):
                    return str(error.get("message") or error)
                if isinstance(error, str):
                    return error
        except ValueError:
            pass
        text = response.text.strip()
        return text[:200] if text else "Unknown error"

    @staticmethod
    def _extract_content(data: dict[str, Any]) -> str:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        first = choices[0]
        if not isinstance(first, dict):
            return ""
        message = first.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        return content.strip() if isinstance(content, str) else ""

    def _call_openrouter_sync(self, prompt: str) -> str:
        payload = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": OPENROUTER_MAX_TOKENS,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                OPENROUTER_CHAT_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except Timeout as exc:
            raise AIServiceError("OpenRouter request timed out.") from exc
        except RequestException as exc:
            logger.exception("OpenRouter connection error")
            raise AIServiceError(f"OpenRouter connection failed: {exc}") from exc

        if response.status_code == 429:
            raise AIServiceError(
                "OpenRouter rate limit exceeded. Please try again later."
            )

        if not response.ok:
            detail = self._extract_error_detail(response)
            logger.error(
                "OpenRouter API error: status=%s detail=%s",
                response.status_code,
                detail,
            )
            raise AIServiceError(
                f"OpenRouter API failed ({response.status_code}): {detail}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise AIServiceError("OpenRouter returned invalid JSON.") from exc

        if not isinstance(data, dict):
            raise AIServiceError("OpenRouter returned an unexpected response format.")

        content = self._extract_content(data)
        if not content:
            raise AIServiceError("OpenRouter returned an empty response.")
        return content

    async def generate_study_material(
        self,
        text: str,
        title: str = "Study Material",
        use_cache: bool = True,
    ) -> Material:
        if not text or not text.strip():
            raise AIServiceError("No text provided for AI processing.")

        key = self.cache_key(text)

        if use_cache and self.storage:
            cached = await self.storage.get_cache(key)
            if cached and cached.get("raw_response"):
                try:
                    return self._parser.parse(cached["raw_response"], title=title)
                except ValueError:
                    logger.warning("Cached AI response invalid, regenerating.")

        prompt = self._build_prompt(text)
        raw = await asyncio.to_thread(self._call_openrouter_sync, prompt)

        if use_cache and self.storage:
            await self.storage.set_cache(
                key,
                {"raw_response": raw, "title": title},
            )

        return self._parser.parse(raw, title=title)
