"""Reply keyboard (bottom menu) button handlers."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from handlers.materials import _show_materials_list
from handlers.profile import _send_leaderboard, _send_profile
from keyboards.menus import (
    ALL_MENU_BUTTON_TEXTS,
    BTN_FLASHCARDS,
    BTN_LEADERBOARD,
    BTN_MOTIVATION,
    BTN_MOTIVATION_LEGACY,
    BTN_MY_MATERIALS,
    BTN_PROFILE,
    BTN_QUIZ,
    BTN_QUIZ_LEGACY,
    BTN_UPLOAD,
    main_keyboard,
    quiz_materials_keyboard,
    flashcards_materials_keyboard,
)
from services.motivation_service import MotivationService
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="reply_menu")


@router.message(F.text == BTN_UPLOAD)
async def btn_upload(message: Message) -> None:
    await message.answer(
        "📤 Send a <b>PDF</b>, <b>PPTX</b>, or <b>TXT</b> file as a document,\n"
        "or paste your study notes as text.",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_MY_MATERIALS)
async def btn_my_materials(message: Message, study: StudyService) -> None:
    try:
        await _show_materials_list(message, study, edit=False)
    except Exception:
        logger.exception("my materials button error")
        await message.answer(
            "⚠️ Could not load materials.",
            reply_markup=main_keyboard(),
        )


@router.message(F.text == BTN_FLASHCARDS)
async def btn_flashcards(message: Message, study: StudyService) -> None:
    try:
        user = await study.get_user(message.from_user.id)
        fc_materials = [m for m in user.materials if m.flashcards]
        if not fc_materials:
            await message.answer(
                "No flashcards yet. Upload study content first!",
                reply_markup=main_keyboard(),
            )
            return
        items = [(m.material_id, m.title) for m in fc_materials]
        await message.answer(
            "🃏 <b>Flashcards</b>\nSelect a material:",
            reply_markup=flashcards_materials_keyboard(items),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("flashcards button error")
        await message.answer(
            "⚠️ Could not load flashcards.",
            reply_markup=main_keyboard(),
        )


@router.message(F.text.in_({BTN_QUIZ, BTN_QUIZ_LEGACY}))
async def btn_quiz(message: Message, study: StudyService) -> None:
    try:
        user = await study.get_user(message.from_user.id)
        quiz_materials = [m for m in user.materials if m.quiz]
        if not quiz_materials:
            await message.answer(
                "You need materials with quizzes first. Upload study content!",
                reply_markup=main_keyboard(),
            )
            return
        items = [(m.material_id, m.title) for m in quiz_materials]
        await message.answer(
            "❓ <b>Quiz</b>\nSelect material:",
            reply_markup=quiz_materials_keyboard(items),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("quiz button error")
        await message.answer(
            "⚠️ Could not load quizzes.",
            reply_markup=main_keyboard(),
        )


@router.message(F.text == BTN_PROFILE)
async def btn_profile(message: Message, study: StudyService) -> None:
    await _send_profile(message, study, edit=False)


@router.message(F.text == BTN_LEADERBOARD)
async def btn_leaderboard(message: Message, study: StudyService) -> None:
    await _send_leaderboard(message, study, edit=False)


@router.message(F.text.in_({BTN_MOTIVATION, BTN_MOTIVATION_LEGACY}))
async def btn_motivation(message: Message, study: StudyService) -> None:
    try:
        user = await study.get_user(message.from_user.id)
        text = MotivationService.daily_message(user.user_id, user.streak)
        await message.answer(
            f"💪 <b>Daily Motivation</b>\n\n{text}",
            reply_markup=main_keyboard(),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("motivation button error")
        await message.answer(
            "⚠️ Could not load motivation. Try again later.",
            reply_markup=main_keyboard(),
        )

