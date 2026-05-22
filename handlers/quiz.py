"""Interactive quiz with inline buttons."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from handlers.utils import answer_callback
from keyboards.callback_data import QuizCallback
from keyboards.menus import quiz_answer_keyboard
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="quiz")


@router.callback_query(F.data.startswith(QuizCallback.START_PREFIX))
async def cb_quiz_start(callback: CallbackQuery, study: StudyService) -> None:
    try:
        material_id = callback.data.split(":", 1)[1]
        user = await study.get_user(callback.from_user.id)
        material = user.get_material(material_id)
        if not material or not material.quiz:
            await answer_callback(callback, "Quiz not found.", show_alert=True)
            return

        session = study.start_quiz_session(callback.from_user.id, material)
        await _send_question(callback, session)
        await answer_callback(callback)
    except Exception:
        logger.exception("quiz start error")
        await answer_callback(callback, "Could not start quiz.", show_alert=True)


async def _send_question(callback: CallbackQuery, session) -> None:
    q = session.current_question
    if q is None:
        await callback.message.edit_text("Quiz has no questions.")
        return
    await callback.message.edit_text(
        f"🎯 <b>{session.title}</b>\n{session.progress_text()}\n\n"
        f"❓ {q.question}",
        reply_markup=quiz_answer_keyboard(
            session.material_id, session.current_index, q.options
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith(QuizCallback.ANSWER_PREFIX))
async def cb_quiz_answer(callback: CallbackQuery, study: StudyService) -> None:
    try:
        parts = callback.data.split(":")
        if len(parts) < 4:
            await answer_callback(callback, "Invalid.", show_alert=True)
            return
        material_id = parts[1]
        question_index = int(parts[2])
        selected = int(parts[3])

        session = study.get_quiz_session(callback.from_user.id)
        if not session or session.material_id != material_id:
            await answer_callback(callback, "Session expired. Start quiz again.", show_alert=True)
            return
        if session.answered:
            await answer_callback(callback, "Already answered. Wait…", show_alert=True)
            return
        if session.current_index != question_index:
            await answer_callback(callback, "This question is outdated.", show_alert=True)
            return

        correct = session.record_answer(selected)
        q = session.questions[question_index]
        correct_text = q.options[q.correct_index]

        feedback = "✅ Correct!" if correct else f"❌ Wrong. Correct: {correct_text}"
        await answer_callback(callback, feedback[:200], show_alert=not correct)

        session.advance()
        if session.finished:
            user = await study.finalize_quiz(callback.from_user.id, session)
            total = len(session.questions)
            await callback.message.edit_text(
                f"🏁 <b>Quiz Complete!</b>\n\n"
                f"Score: <b>{session.score}/{total}</b>\n"
                f"Points earned: <b>{session.score * 10}</b>\n"
                f"Total score: <b>{user.score}</b>\n"
                f"Streak: <b>{user.streak}</b> 🔥",
                parse_mode="HTML",
            )
        else:
            await _send_question(callback, session)
    except Exception:
        logger.exception("quiz answer error")
        await answer_callback(callback, "Error processing answer.", show_alert=True)
