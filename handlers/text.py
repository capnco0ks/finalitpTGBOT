"""Plain text and URL message handler (study content only — not menu buttons)."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from ai.gemini_service import AIServiceError
from keyboards.menus import ALL_MENU_BUTTON_TEXTS, main_keyboard
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="text")


@router.message(F.text, ~F.text.startswith("/"), ~F.text.in_(ALL_MENU_BUTTON_TEXTS))
async def handle_text(message: Message, study: StudyService) -> None:
    if not message.text:
        return

    text = message.text.strip()
    urls = StudyService.extract_urls(text)

    status = await message.answer(
        "⏳ Processing your content with AI…",
        reply_markup=main_keyboard(),
    )

    try:
        if urls and len(text) < 100:
            material = await study.process_url(message.from_user.id, urls[0])
        else:
            title = "Study Notes"
            if urls:
                title = "Notes + Link"
            material = await study.process_text(message.from_user.id, text, title=title)

        await status.edit_text(
            f"✅ <b>{material.title}</b> saved!\n\n"
            f"📝 {material.summary[:400]}{'…' if len(material.summary) > 400 else ''}\n\n"
            f"🃏 {len(material.flashcards)} flashcards | "
            f"❓ {len(material.quiz)} quiz questions",
            parse_mode="HTML",
        )
    except ValueError as exc:
        await status.edit_text(f"❌ {exc}")
    except AIServiceError as exc:
        logger.warning("AI error: %s", exc)
        await status.edit_text(f"❌ AI error: {exc}")
    except Exception:
        logger.exception("Text processing error")
        await status.edit_text("❌ Could not process text. Please try again.")
