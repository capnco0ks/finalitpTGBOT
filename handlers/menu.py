"""Main menu inline callback handlers."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from handlers.utils import answer_callback
from keyboards.callback_data import MenuCallback
from keyboards.menus import (
    flashcards_materials_keyboard,
    main_keyboard,
    quiz_materials_keyboard,
    start_inline_keyboard,
)
from services.motivation_service import MotivationService
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="menu")


@router.callback_query(F.data == MenuCallback.MAIN)
async def cb_main_menu(callback: CallbackQuery) -> None:
    try:
        await callback.message.edit_text(
            "🏠 <b>Main Menu</b>\nChoose an option:",
            reply_markup=start_inline_keyboard(),
            parse_mode="HTML",
        )
        await callback.message.answer(
            "Main menu — use the buttons below:",
            reply_markup=main_keyboard(),
        )
    except Exception:
        logger.warning("main menu edit failed, user=%s", callback.from_user.id)
        await callback.message.answer(
            "🏠 <b>Main Menu</b>",
            reply_markup=main_keyboard(),
            parse_mode="HTML",
        )
    await answer_callback(callback)


@router.callback_query(F.data == MenuCallback.QUIZ)
async def cb_menu_quiz(callback: CallbackQuery, study: StudyService) -> None:
    try:
        user = await study.get_user(callback.from_user.id)
        quiz_materials = [m for m in user.materials if m.quiz]
        if not quiz_materials:
            await callback.message.edit_text(
                "No quiz materials yet. Upload content first!",
                reply_markup=start_inline_keyboard(),
            )
            await answer_callback(callback)
            return
        items = [(m.material_id, m.title) for m in quiz_materials]
        await callback.message.edit_text(
            "❓ <b>Quiz</b>\nSelect material:",
            reply_markup=quiz_materials_keyboard(items),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("menu:quiz error user=%s", callback.from_user.id)
        await answer_callback(callback, "Could not open quiz menu.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data == MenuCallback.FLASHCARDS)
async def cb_menu_flashcards(callback: CallbackQuery, study: StudyService) -> None:
    try:
        user = await study.get_user(callback.from_user.id)
        fc_materials = [m for m in user.materials if m.flashcards]
        if not fc_materials:
            await callback.message.edit_text(
                "No flashcards yet. Upload study content first!",
                reply_markup=start_inline_keyboard(),
            )
            await answer_callback(callback)
            return
        items = [(m.material_id, m.title) for m in fc_materials]
        await callback.message.edit_text(
            "🃏 <b>Flashcards</b>\nSelect material:",
            reply_markup=flashcards_materials_keyboard(items),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("menu:flashcards error user=%s", callback.from_user.id)
        await answer_callback(callback, "Could not open flashcards.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data == MenuCallback.PROFILE)
async def cb_menu_profile(callback: CallbackQuery, study: StudyService) -> None:
    from handlers.profile import _send_profile

    try:
        await _send_profile(
            callback.message,
            study,
            edit=True,
            user_id=callback.from_user.id,
        )
    except Exception:
        logger.exception("menu:profile error user=%s", callback.from_user.id)
        await answer_callback(callback, "Could not load profile.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data == MenuCallback.LEADERBOARD)
async def cb_menu_leaderboard(callback: CallbackQuery, study: StudyService) -> None:
    from handlers.profile import _send_leaderboard

    try:
        await _send_leaderboard(callback.message, study, edit=True)
    except Exception:
        logger.exception("menu:leaderboard error user=%s", callback.from_user.id)
        await answer_callback(callback, "Could not load leaderboard.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data == MenuCallback.MOTIVATION)
async def cb_menu_motivation(callback: CallbackQuery, study: StudyService) -> None:
    try:
        user = await study.get_user(callback.from_user.id)
        quote = MotivationService.daily_message(user.user_id, user.streak)
        await callback.message.edit_text(
            f"💪 <b>Daily Motivation</b>\n\n{quote}",
            reply_markup=start_inline_keyboard(),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("menu:motivation error user=%s", callback.from_user.id)
        await answer_callback(callback, "Could not load motivation.", show_alert=True)
        return
    await answer_callback(callback)
