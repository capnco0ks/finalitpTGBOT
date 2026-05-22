from __future__ import annotations

import logging

from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)


async def answer_callback(
    callback: CallbackQuery,
    text: str | None = None,
    *,
    show_alert: bool = False,
) -> None:
    try:
        await callback.answer(text, show_alert=show_alert)
    except Exception:
        logger.debug("callback.answer skipped (id=%s)", callback.id)
