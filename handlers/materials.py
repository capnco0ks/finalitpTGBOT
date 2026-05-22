"""My Materials, summaries, and flashcards."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from handlers.utils import answer_callback
from keyboards.callback_data import MaterialCallback, MenuCallback
from keyboards.menus import (
    flashcard_keyboard,
    main_keyboard,
    material_actions_keyboard,
    materials_list_keyboard,
)
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="materials")


async def _show_materials_list(target: Message, study: StudyService, edit: bool = False) -> None:
    user_id = target.chat.id
    user = await study.get_user(user_id)

    if not user.materials:
        text = "📚 You have no materials yet.\nUpload a file or send text to get started!"
        if edit:
            await target.edit_text(text)
        else:
            await target.answer(text, reply_markup=main_keyboard())
        return

    items = [(m.material_id, m.title) for m in user.materials]
    text = "📚 <b>My Materials</b>\nSelect a material:"
    kb = materials_list_keyboard(items)
    if edit:
        await target.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == MenuCallback.MATERIALS)
async def cb_materials(callback: CallbackQuery, study: StudyService) -> None:
    try:
        await _show_materials_list(callback.message, study, edit=True)
    except Exception:
        logger.exception("materials callback error")
        await answer_callback(callback, "Error loading materials.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data.startswith(MaterialCallback.PREFIX))
async def cb_material_detail(callback: CallbackQuery, study: StudyService) -> None:
    try:
        material_id = callback.data.split(":", 1)[1]
        user = await study.get_user(callback.from_user.id)
        material = user.get_material(material_id)
        if not material:
            await answer_callback(callback, "Material not found.", show_alert=True)
            return
        await callback.message.edit_text(
            f"📖 <b>{material.title}</b>\n\n"
            f"🃏 Flashcards: {len(material.flashcards)}\n"
            f"🎯 Quiz: {len(material.quiz)} questions",
            reply_markup=material_actions_keyboard(material_id),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("material detail error")
        await answer_callback(callback, "Error.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data.startswith(MaterialCallback.SUMMARY_PREFIX))
async def cb_summary(callback: CallbackQuery, study: StudyService) -> None:
    try:
        material_id = callback.data.split(":", 1)[1]
        user = await study.get_user(callback.from_user.id)
        material = user.get_material(material_id)
        if not material:
            await answer_callback(callback, "Not found.", show_alert=True)
            return
        summary = material.summary
        if len(summary) > 3500:
            summary = summary[:3500] + "…"
        await callback.message.edit_text(
            f"📝 <b>Summary — {material.title}</b>\n\n{summary}",
            reply_markup=material_actions_keyboard(material_id),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("summary error")
        await answer_callback(callback, "Error.", show_alert=True)
        return
    await answer_callback(callback)


@router.callback_query(F.data.startswith(MaterialCallback.FLASHCARD_PREFIX))
async def cb_flashcards(callback: CallbackQuery, study: StudyService) -> None:
    try:
        parts = callback.data.split(":")
        if len(parts) < 4:
            await answer_callback(callback, "Invalid.", show_alert=True)
            return
        material_id = parts[1]
        index = int(parts[2])
        mode = parts[3]
        show_answer = mode == "a"

        user = await study.get_user(callback.from_user.id)
        material = user.get_material(material_id)
        if not material or not material.flashcards:
            await answer_callback(callback, "No flashcards.", show_alert=True)
            return

        index = max(0, min(index, len(material.flashcards) - 1))
        card = material.flashcards[index]
        label = "Answer" if show_answer else "Question"
        content = card.answer if show_answer else card.question

        await callback.message.edit_text(
            f"🃏 <b>{material.title}</b> — Card {index + 1}/{len(material.flashcards)}\n\n"
            f"<b>{label}:</b>\n{content}",
            reply_markup=flashcard_keyboard(
                material_id, index, len(material.flashcards), show_answer
            ),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("flashcard error")
        await answer_callback(callback, "Error.", show_alert=True)
        return
    await answer_callback(callback)
