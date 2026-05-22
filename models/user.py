
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from models.material import Material


@dataclass
class User:
    user_id: int
    username: str | None = None
    first_name: str | None = None
    score: int = 0
    streak: int = 0
    last_active: str | None = None
    materials: list[Material] = field(default_factory=list)

    @property
    def material_count(self) -> int:
        return len(self.materials)

    def add_material(self, material: Material) -> None:
        self.materials.append(material)

    def get_material(self, material_id: str) -> Material | None:
        for material in self.materials:
            if material.material_id == material_id:
                return material
        return None

    def update_streak(self, today: date | None = None) -> int:
        today = today or date.today()
        today_str = today.isoformat()
        if self.last_active == today_str:
            return self.streak
        if self.last_active:
            try:
                last = date.fromisoformat(self.last_active)
                delta = (today - last).days
                if delta == 1:
                    self.streak += 1
                elif delta > 1:
                    self.streak = 1
            except ValueError:
                self.streak = 1
        else:
            self.streak = 1
        self.last_active = today_str
        return self.streak

    def add_quiz_score(self, points: int) -> None:
        self.score += max(0, points)

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "first_name": self.first_name,
            "score": self.score,
            "streak": self.streak,
            "last_active": self.last_active,
            "materials": [m.to_dict() for m in self.materials],
        }

    @classmethod
    def from_dict(cls, user_id: int, data: dict[str, Any]) -> User:
        materials = [
            Material.from_dict(m) for m in data.get("materials", []) if isinstance(m, dict)
        ]
        return cls(
            user_id=user_id,
            username=data.get("username"),
            first_name=data.get("first_name"),
            score=int(data.get("score", 0)),
            streak=int(data.get("streak", 0)),
            last_active=data.get("last_active"),
            materials=materials,
        )
