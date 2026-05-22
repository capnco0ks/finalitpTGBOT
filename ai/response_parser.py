"""Parse structured JSON from AI responses into domain objects."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from config import FLASHCARD_COUNT, MAX_SUMMARY_CHARS, QUIZ_QUESTION_COUNT
from models.material import Flashcard, Material, QuizQuestion

logger = logging.getLogger(__name__)

_MAX_QUESTION_LEN = 200
_MAX_ANSWER_LEN = 120
_MAX_OPTION_LEN = 60


class AIResponseParser:
    """Converts raw AI text into Material components."""

    @staticmethod
    def _extract_json_block(text: str) -> str:
        text = text.strip()
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if fence:
            return fence.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text

    @classmethod
    def parse(cls, raw_response: str, title: str = "Study Material") -> Material:
        if not raw_response or not raw_response.strip():
            raise ValueError("Empty response from AI.")

        json_text = cls._extract_json_block(raw_response)
        try:
            data: dict[str, Any] = json.loads(json_text)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse AI JSON: %s", exc)
            raise ValueError("AI returned invalid JSON.") from exc

        summary = str(data.get("summary", "")).strip()[:MAX_SUMMARY_CHARS]
        if not summary:
            raise ValueError("AI response missing summary.")

        flashcards_raw = data.get("flashcards", [])
        flashcards: list[Flashcard] = []
        if isinstance(flashcards_raw, list):
            for item in flashcards_raw:
                if len(flashcards) >= FLASHCARD_COUNT:
                    break
                if not isinstance(item, dict) or not item.get("question") or not item.get("answer"):
                    continue
                flashcards.append(
                    Flashcard(
                        question=str(item["question"])[:_MAX_QUESTION_LEN],
                        answer=str(item["answer"])[:_MAX_ANSWER_LEN],
                    )
                )

        quiz_raw = data.get("quiz", [])
        quiz: list[QuizQuestion] = []
        if isinstance(quiz_raw, list):
            for item in quiz_raw:
                if len(quiz) >= QUIZ_QUESTION_COUNT:
                    break
                if not isinstance(item, dict):
                    continue
                options = item.get("options", [])
                if not isinstance(options, list) or len(options) < 2:
                    continue
                options = [str(o)[:_MAX_OPTION_LEN] for o in options[:4]]
                correct = item.get("correct_index", item.get("correct", 0))
                try:
                    correct_index = int(correct)
                except (TypeError, ValueError):
                    correct_index = 0
                if 0 <= correct_index < len(options) and item.get("question"):
                    quiz.append(
                        QuizQuestion(
                            question=str(item["question"])[:_MAX_QUESTION_LEN],
                            options=options,
                            correct_index=correct_index,
                        )
                    )

        if not flashcards:
            raise ValueError("AI response contained no valid flashcards.")
        if not quiz:
            raise ValueError("AI response contained no valid quiz questions.")

        return Material(
            title=title,
            summary=summary,
            flashcards=flashcards,
            quiz=quiz,
        )
