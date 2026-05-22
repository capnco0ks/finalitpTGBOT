"""Start command."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.menus import main_keyboard
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="start")

WELCOME = (
    "👋 <b>Welcome to AI Study Assistant!</b>\n\n"
    "Upload <b>PDF</b>, <b>PPTX</b>, or <b>TXT</b> files, send text, or share a link.\n"
    "I'll generate summaries, flashcards, and quizzes for you.\n\n"
    "Tap the buttons at the bottom of the chat to navigate."
)


@router.message(CommandStart())
async def cmd_start(message: Message, study: StudyService) -> None:
    keyboard = main_keyboard()
    try:
        user = await study.ensure_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
        await message.answer(
            f"{WELCOME}\n\n"
            f"📊 Materials: <b>{user.material_count}</b> | "
            f"Score: <b>{user.score}</b> | Streak: <b>{user.streak}</b> 🔥",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("start command error")
        await message.answer(
            "⚠️ Something went wrong. Please try /start again.",
            reply_markup=keyboard,
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Commands</b>\n"
        "/start — Show main keyboard\n"
        "/help — This message\n\n"
        "Use the bottom menu buttons to upload files, view materials, "
        "flashcards, quizzes, profile, and leaderboard.",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )
