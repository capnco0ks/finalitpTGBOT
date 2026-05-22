"""Document upload handler."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.types import Message

from config import MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS
from parsers import ParserError
from services.study_service import StudyService

logger = logging.getLogger(__name__)
router = Router(name="documents")


@router.message(F.document)
async def handle_document(message: Message, study: StudyService) -> None:
    document = message.document
    if not document:
        return

    file_name = document.file_name or "upload"
    suffix = Path(file_name).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        await message.answer(
            f"❌ Unsupported file type <b>{suffix or 'unknown'}</b>.\n"
            f"Supported: PDF, PPTX, TXT",
            parse_mode="HTML",
        )
        return

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if document.file_size and document.file_size > max_bytes:
        await message.answer(f"❌ File too large. Max size: {MAX_FILE_SIZE_MB} MB.")
        return

    status = await message.answer("⏳ Downloading and processing your file…")

    tmp_path: Path | None = None
    try:
        bot = message.bot
        file = await bot.get_file(document.file_id)
        suffix = Path(file_name).suffix or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = Path(tmp.name)
            await bot.download_file(file.file_path, tmp)

        material = await study.process_file(
            message.from_user.id,
            tmp_path,
            title=Path(file_name).stem,
        )
        await status.edit_text(
            f"✅ <b>{material.title}</b> processed!\n\n"
            f"📝 Summary preview:\n{material.summary[:400]}"
            f"{'…' if len(material.summary) > 400 else ''}\n\n"
            f"🃏 Flashcards: {len(material.flashcards)}\n"
            f"🎯 Quiz questions: {len(material.quiz)}\n\n"
            "Open <b>My Materials</b> to review everything.",
            parse_mode="HTML",
        )
    except ParserError as exc:
        logger.warning("Parser error: %s", exc)
        await status.edit_text(f"❌ Could not read file: {exc}")
    except Exception as exc:
        logger.exception("Document processing failed")
        from ai.gemini_service import AIServiceError

        if isinstance(exc, AIServiceError) or "AIService" in type(exc).__name__:
            await status.edit_text(f"❌ AI processing failed: {exc}")
        else:
            await status.edit_text("❌ Failed to process file. Please try another document.")
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
