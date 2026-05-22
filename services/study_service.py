from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp

from ai.gemini_service import AIService, AIServiceError
from config import MAX_TEXT_LENGTH
from models.material import Material
from models.quiz import Quiz, QuizSession
from models.user import User
from parsers import ParserError, ParserFactory

if TYPE_CHECKING:
    from storage.json_storage import JSONStorage

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


class StudyService:

    def __init__(self, storage: JSONStorage, ai_service: AIService) -> None:
        self.storage = storage
        self.ai = ai_service
        self._quiz_sessions: dict[int, QuizSession] = {}

    async def ensure_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> User:
        user = await self.storage.update_user_profile(user_id, username, first_name)
        user.update_streak()
        await self.storage.save_user(user)
        return user

    async def process_file(self, user_id: int, file_path: Path, title: str | None = None) -> Material:
        try:
            text = ParserFactory.extract_text(file_path)
        except ParserError:
            raise
        except Exception as exc:
            logger.exception("Unexpected parser error")
            raise ParserError(f"Could not process file: {exc}") from exc

        return await self._generate_and_save(user_id, text, title or file_path.stem)

    async def process_text(self, user_id: int, text: str, title: str = "Text Note") -> Material:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Text is empty.")
        if len(cleaned) > MAX_TEXT_LENGTH:
            cleaned = cleaned[:MAX_TEXT_LENGTH]
        return await self._generate_and_save(user_id, cleaned, title)

    async def process_url(self, user_id: int, url: str) -> Material:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=15),
                    headers={"User-Agent": "StudyAssistantBot/1.0"},
                ) as resp:
                    if resp.status != 200:
                        raise ValueError(f"URL returned status {resp.status}.")
                    html = await resp.text(errors="ignore")
        except aiohttp.ClientError as exc:
            raise ValueError(f"Could not fetch URL: {exc}") from exc

        text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
        text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 50:
            raise ValueError("Could not extract enough text from the link.")
        return await self.process_text(user_id, text[:MAX_TEXT_LENGTH], title="Web Page")

    async def _generate_and_save(self, user_id: int, text: str, title: str) -> Material:
        try:
            material = await self.ai.generate_study_material(text, title=title)
        except AIServiceError:
            raise
        except ValueError as exc:
            raise AIServiceError(str(exc)) from exc

        user = await self.storage.add_material(user_id, material)
        user.update_streak()
        await self.storage.save_user(user)
        return material

    async def get_user(self, user_id: int) -> User:
        return await self.storage.get_user(user_id)

    def start_quiz_session(self, user_id: int, material: Material) -> QuizSession:
        session = QuizSession(
            user_id=user_id,
            material_id=material.material_id,
            title=material.title,
            questions=material.quiz,
        )
        self._quiz_sessions[user_id] = session
        return session

    def get_quiz_session(self, user_id: int) -> QuizSession | None:
        return self._quiz_sessions.get(user_id)

    def end_quiz_session(self, user_id: int) -> QuizSession | None:
        return self._quiz_sessions.pop(user_id, None)

    async def finalize_quiz(self, user_id: int, session: QuizSession) -> User:
        user = await self.storage.get_user(user_id)
        user.add_quiz_score(session.score * 10)
        user.update_streak()
        await self.storage.save_user(user)
        self.end_quiz_session(user_id)
        return user

    @staticmethod
    def build_quiz(material: Material) -> Quiz:
        return Quiz(
            material_id=material.material_id,
            title=material.title,
            questions=material.quiz,
        )

    @staticmethod
    def extract_urls(message_text: str) -> list[str]:
        return URL_PATTERN.findall(message_text)
