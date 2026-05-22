"""Quiz session state for interactive Telegram quizzes."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.material import QuizQuestion


@dataclass
class Quiz:
    """Collection of quiz questions tied to a material."""

    material_id: str
    title: str
    questions: list[QuizQuestion]

    @property
    def total(self) -> int:
        return len(self.questions)


@dataclass
class QuizSession:
    """Tracks an in-progress interactive quiz for one user."""

    user_id: int
    material_id: str
    title: str
    questions: list[QuizQuestion]
    current_index: int = 0
    score: int = 0
    answered: bool = False

    @property
    def finished(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def current_question(self) -> QuizQuestion | None:
        if self.finished:
            return None
        return self.questions[self.current_index]

    def record_answer(self, selected_index: int) -> bool:
        """Record answer; returns True if correct."""
        if self.finished or self.answered:
            return False
        question = self.current_question
        if question is None:
            return False
        correct = selected_index == question.correct_index
        if correct:
            self.score += 1
        self.answered = True
        return correct

    def advance(self) -> None:
        self.current_index += 1
        self.answered = False

    def progress_text(self) -> str:
        return f"Question {min(self.current_index + 1, len(self.questions))}/{len(self.questions)}"
