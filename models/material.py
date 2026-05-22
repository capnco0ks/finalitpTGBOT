"""Domain models for study materials."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Flashcard:
    question: str
    answer: str

    def to_dict(self) -> dict[str, str]:
        return {"question": self.question, "answer": self.answer}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Flashcard:
        return cls(
            question=str(data.get("question", "")),
            answer=str(data.get("answer", "")),
        )


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    correct_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "options": self.options,
            "correct_index": self.correct_index,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuizQuestion:
        options = data.get("options", [])
        if not isinstance(options, list):
            options = []
        return cls(
            question=str(data.get("question", "")),
            options=[str(o) for o in options],
            correct_index=int(data.get("correct_index", 0)),
        )


@dataclass
class Material:
    title: str
    summary: str
    flashcards: list[Flashcard] = field(default_factory=list)
    quiz: list[QuizQuestion] = field(default_factory=list)
    material_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.material_id,
            "title": self.title,
            "summary": self.summary,
            "flashcards": [f.to_dict() for f in self.flashcards],
            "quiz": [q.to_dict() for q in self.quiz],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Material:
        flashcards = [
            Flashcard.from_dict(f) for f in data.get("flashcards", []) if isinstance(f, dict)
        ]
        quiz = [
            QuizQuestion.from_dict(q) for q in data.get("quiz", []) if isinstance(q, dict)
        ]
        return cls(
            material_id=str(data.get("id", uuid.uuid4())[:8]),
            title=str(data.get("title", "Untitled")),
            summary=str(data.get("summary", "")),
            flashcards=flashcards,
            quiz=quiz,
        )
