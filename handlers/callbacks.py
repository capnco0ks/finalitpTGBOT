"""Fallback handler for unmatched callback queries."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from handlers.utils import answer_callback

logger = logging.getLogger(__name__)
router = Router(name="callbacks_fallback")


@router.callback_query()
async def cb_unhandled(callback: CallbackQuery) -> None:
    logger.warning(
        "Unhandled callback_query: user_id=%s data=%r",
        callback.from_user.id,
        callback.data,
    )
    await answer_callback(callback, "This button is not available.", show_alert=True)
