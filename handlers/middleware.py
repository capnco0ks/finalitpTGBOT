"""Dispatcher middleware."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from services.study_service import StudyService

logger = logging.getLogger(__name__)


class CallbackLogMiddleware(BaseMiddleware):
    """Log every callback_query before handlers run."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery):
            logger.info(
                "callback_query received: user_id=%s chat_id=%s data=%r",
                event.from_user.id,
                event.message.chat.id if event.message else None,
                event.data,
            )
        return await handler(event, data)


class StudyServiceMiddleware(BaseMiddleware):
    def __init__(self, study_service: StudyService) -> None:
        self.study_service = study_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["study"] = self.study_service
        return await handler(event, data)