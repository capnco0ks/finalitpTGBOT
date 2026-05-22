
from __future__ import annotations

import logging
from datetime import date, timedelta

from aiogram import Router
from aiogram.types import Message

from keyboards.menus import main_keyboard
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="profile")


async def _send_profile(
    message: Message,
    study: StudyService,
    edit: bool,
    user_id: int | None = None,
) -> None:
    try:
        uid = user_id or message.chat.id
        user = await study.get_user(uid)
        user.update_streak()
        await study.storage.save_user(user)
        text = (
            f"👤 <b>Profile</b>\n\n"
            f"Name: {user.first_name or '—'}\n"
        )
        if user.username:
            text += f"Username: @{user.username}\n"
        text += (
            f"📚 Materials: <b>{user.material_count}</b>\n"
            f"🏆 Total score: <b>{user.score}</b>\n"
            f"🔥 Streak: <b>{user.streak}</b> days"
        )
        if edit:
            await message.edit_text(text, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=main_keyboard(), parse_mode="HTML")
    except Exception:
        logger.exception("profile error")
        msg = "⚠️ Could not load profile."
        if edit:
            await message.edit_text(msg)
        else:
            await message.answer(msg, reply_markup=main_keyboard())


async def _send_leaderboard(message: Message, study: StudyService, edit: bool) -> None:
    try:
        entries = await study.storage.get_leaderboard(10)
        if not entries:
            text = "🏆 <b>Leaderboard</b>\n\nNo scores yet. Complete a quiz!"
        else:
            lines = ["🏆 <b>Leaderboard</b>\n"]
            medals = ["🥇", "🥈", "🥉"]
            for i, (_, name, score, streak) in enumerate(entries):
                medal = medals[i] if i < 3 else f"{i + 1}."
                lines.append(f"{medal} {name} — {score} pts (🔥{streak})")
            text = "\n".join(lines)
        if edit:
            await message.edit_text(text, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=main_keyboard(), parse_mode="HTML")
    except Exception:
        logger.exception("leaderboard error")
        msg = "⚠️ Could not load leaderboard."
        if edit:
            await message.edit_text(msg)
        else:
            await message.answer(msg, reply_markup=main_keyboard())


async def _send_schedule(
    message: Message,
    study: StudyService,
    edit: bool,
    user_id: int | None = None,
    reply_markup=None,
) -> None:
    try:
        uid = user_id or message.chat.id
        user = await study.get_user(uid)
        user.update_streak()
        await study.storage.save_user(user)

        today = date.today()
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        week_lines = []
        for i in range(7):
            day = today + timedelta(days=i)
            label = days[day.weekday()]
            if i == 0:
                label = f"Today ({label})"
            task = (
                "Review 1 saved material + 1 quiz"
                if user.materials
                else "Upload your first study material"
            )
            week_lines.append(f"• <b>{label}</b> ({day.strftime('%d %b')}): {task}")

        text = (
            "📅 <b>Study Schedule</b>\n\n"
            f"🔥 Streak: <b>{user.streak}</b> day(s)\n"
            f"📚 Materials: <b>{user.material_count}</b>\n\n"
            "<b>This week</b>\n"
            + "\n".join(week_lines)
        )
        if edit:
            await message.edit_text(
                text, parse_mode="HTML", reply_markup=reply_markup
            )
        else:
            await message.answer(
                text, parse_mode="HTML", reply_markup=reply_markup
            )
    except Exception:
        logger.exception("schedule error")
        msg = "⚠️ Could not load schedule."
        if edit:
            await message.edit_text(msg, reply_markup=reply_markup)
        else:
            await message.answer(msg, reply_markup=reply_markup)
