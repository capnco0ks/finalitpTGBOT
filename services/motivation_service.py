"""Daily motivation messages (bonus feature)."""

from __future__ import annotations

import random
from datetime import date

MOTIVATIONS = [
    "Small steps every day beat cramming once a week. You've got this! 💪",
    "Your future self will thank you for studying today. 📖",
    "Mistakes are proof you're learning. Keep going! 🌟",
    "Consistency beats intensity. One flashcard at a time. 🃏",
    "The expert in anything was once a beginner. Stay curious! 🔍",
    "Progress, not perfection. Review one quiz today! 🎯",
    "Your brain is a muscle — train it daily. 🧠",
    "Every question you answer makes the next one easier. ✨",
]


class MotivationService:
    """Provides deterministic daily motivation per user."""

    @classmethod
    def daily_message(cls, user_id: int, streak: int = 0) -> str:
        today = date.today().isoformat()
        seed = hash(f"{user_id}:{today}") % (2**32)
        rng = random.Random(seed)
        base = rng.choice(MOTIVATIONS)
        if streak > 1:
            return f"{base}\n\n🔥 Streak: {streak} days — amazing!"
        return base
