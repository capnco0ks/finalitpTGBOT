from __future__ import annotations

import asyncio
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from models.material import Material
from models.user import User

logger = logging.getLogger(__name__)


class JSONStorage:

    def __init__(self, users_path: Path, cache_path: Path | None = None) -> None:
        self.users_path = users_path
        self.cache_path = cache_path
        self._lock = asyncio.Lock()
        self._ensure_files()

    def _ensure_files(self) -> None:
        self.users_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.users_path.exists():
            self._write_sync(self.users_path, {})
        if self.cache_path and not self.cache_path.exists():
            self._write_sync(self.cache_path, {})

    @staticmethod
    def _read_sync(path: Path) -> dict[str, Any]:
        try:
            raw = path.read_text(encoding="utf-8").strip()
            if not raw:
                return {}
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError as exc:
            logger.error("JSON corruption in %s: %s", path, exc)
            backup = path.with_suffix(
                f".corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                shutil.copy2(path, backup)
                logger.warning("Corrupt file backed up to %s", backup)
            except OSError:
                pass
            return {}
        except OSError as exc:
            logger.error("Cannot read %s: %s", path, exc)
            return {}

    @staticmethod
    def _write_sync(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temp.replace(path)

    async def _load_users_raw(self) -> dict[str, Any]:
        async with self._lock:
            return await asyncio.to_thread(self._read_sync, self.users_path)

    async def _save_users_raw(self, data: dict[str, Any]) -> None:
        async with self._lock:
            await asyncio.to_thread(self._write_sync, self.users_path, data)

    async def get_user(self, user_id: int) -> User:
        data = await self._load_users_raw()
        key = str(user_id)
        if key not in data:
            return User(user_id=user_id)
        return User.from_dict(user_id, data[key])

    async def save_user(self, user: User) -> None:
        data = await self._load_users_raw()
        data[str(user.user_id)] = user.to_dict()
        await self._save_users_raw(data)

    async def add_material(self, user_id: int, material: Material) -> User:
        user = await self.get_user(user_id)
        user.add_material(material)
        await self.save_user(user)
        return user

    async def update_user_profile(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> User:
        user = await self.get_user(user_id)
        if username is not None:
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        await self.save_user(user)
        return user

    async def get_leaderboard(self, limit: int = 10) -> list[tuple[int, str, int, int]]:
        data = await self._load_users_raw()
        entries: list[tuple[int, str, int, int]] = []
        for key, value in data.items():
            if not isinstance(value, dict):
                continue
            try:
                uid = int(key)
            except ValueError:
                continue
            name = value.get("first_name") or value.get("username") or f"User {uid}"
            score = int(value.get("score", 0))
            streak = int(value.get("streak", 0))
            entries.append((uid, str(name), score, streak))
        entries.sort(key=lambda x: (x[2], x[3]), reverse=True)
        return entries[:limit]

    async def get_cache(self, cache_key: str) -> dict[str, Any] | None:
        if not self.cache_path:
            return None
        async with self._lock:
            cache = await asyncio.to_thread(self._read_sync, self.cache_path)
        entry = cache.get(cache_key)
        return entry if isinstance(entry, dict) else None

    async def set_cache(self, cache_key: str, payload: dict[str, Any]) -> None:
        if not self.cache_path:
            return
        async with self._lock:
            cache = await asyncio.to_thread(self._read_sync, self.cache_path)
            cache[cache_key] = payload
            await asyncio.to_thread(self._write_sync, self.cache_path, cache)
