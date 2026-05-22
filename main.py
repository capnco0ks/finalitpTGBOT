"""
AI Study Assistant — application entry point.

Run: python main.py
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

import config
from ai.gemini_service import AIService, AIServiceError
from handlers.callbacks import router as callbacks_fallback_router
from handlers.documents import router as documents_router
from handlers.materials import router as materials_router
from handlers.menu import router as menu_router
from handlers.middleware import CallbackLogMiddleware, StudyServiceMiddleware
from handlers.profile import router as profile_router
from handlers.quiz import router as quiz_router
from handlers.reply_menu import router as reply_menu_router
from handlers.start import router as start_router
from handlers.text import router as text_router
from keyboards.menus import main_keyboard
from services.study_service import StudyService
from storage.json_storage import JSONStorage

logger = logging.getLogger(__name__)


def validate_config() -> None:
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Set it in .env")
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Set it in .env")


async def on_error(event: ErrorEvent) -> None:
    logger.exception(
        "Unhandled error: %s",
        event.exception,
        exc_info=event.exception,
    )
    update = event.update
    try:
        if update.message:
            await update.message.answer(
                "⚠️ An unexpected error occurred. The bot is still running — please try again.",
                reply_markup=main_keyboard(),
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "Something went wrong. Please try again.",
                show_alert=True,
            )
    except Exception:
        pass


def register_routers(dp: Dispatcher) -> None:
    """Register routers; reply_menu before text so menu buttons are handled."""
    dp.include_router(start_router)
    dp.include_router(reply_menu_router)
    dp.include_router(documents_router)
    dp.include_router(materials_router)
    dp.include_router(quiz_router)
    dp.include_router(profile_router)
    dp.include_router(menu_router)
    dp.include_router(text_router)
    dp.include_router(callbacks_fallback_router)


async def main() -> None:
    validate_config()

    storage = JSONStorage(config.USERS_JSON, config.CACHE_JSON)
    try:
        ai_service = AIService(storage=storage)
    except AIServiceError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    study_service = StudyService(storage, ai_service)

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(disable_fsm=True)
    dp.update.middleware(CallbackLogMiddleware())
    dp.update.middleware(StudyServiceMiddleware(study_service))
    dp.errors.register(on_error)
    register_routers(dp)

    logger.info("Study Assistant bot started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
