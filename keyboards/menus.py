"""Telegram keyboard builders."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from keyboards.callback_data import MaterialCallback, MenuCallback, QuizCallback

# Reply keyboard button labels (must match handler F.text filters exactly)
BTN_UPLOAD = "📤 Upload Material"
BTN_MY_MATERIALS = "📚 My Materials"
BTN_FLASHCARDS = "🃏 Flashcards"
BTN_QUIZ = "❓ Quiz"
BTN_PROFILE = "👤 Profile"
BTN_LEADERBOARD = "🏆 Leaderboard"
BTN_MOTIVATION = "💪 Daily Motivation"

# Legacy labels (users with an old keyboard cached in Telegram)
BTN_QUIZ_LEGACY = "🎯 Start Quiz"
BTN_MOTIVATION_LEGACY = "💡 Daily Motivation"

ALL_MENU_BUTTON_TEXTS = frozenset(
    {
        BTN_UPLOAD,
        BTN_MY_MATERIALS,
        BTN_FLASHCARDS,
        BTN_QUIZ,
        BTN_PROFILE,
        BTN_LEADERBOARD,
        BTN_MOTIVATION,
        BTN_QUIZ_LEGACY,
        BTN_MOTIVATION_LEGACY,
    }
)


def main_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom reply keyboard for the main menu."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_UPLOAD), KeyboardButton(text=BTN_MY_MATERIALS)],
            [KeyboardButton(text=BTN_FLASHCARDS), KeyboardButton(text=BTN_QUIZ)],
            [KeyboardButton(text=BTN_PROFILE), KeyboardButton(text=BTN_LEADERBOARD)],
            [KeyboardButton(text=BTN_MOTIVATION)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Send a file, text, or link…",
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Alias for main_keyboard()."""
    return main_keyboard()


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Alias for main_keyboard()."""
    return main_keyboard()


def start_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚 My Materials", callback_data=MenuCallback.MATERIALS
                ),
                InlineKeyboardButton(
                    text="❓ Quiz", callback_data=MenuCallback.QUIZ
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🃏 Flashcards", callback_data=MenuCallback.FLASHCARDS
                ),
                InlineKeyboardButton(
                    text="👤 Profile", callback_data=MenuCallback.PROFILE
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Leaderboard", callback_data=MenuCallback.LEADERBOARD
                ),
                InlineKeyboardButton(
                    text="💪 Motivation", callback_data=MenuCallback.MOTIVATION
                ),
            ],
        ]
    )


def materials_list_keyboard(materials: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=title[:40], callback_data=f"{MaterialCallback.PREFIX}{mid}"
            )
        ]
        for mid, title in materials
    ]
    rows.append(
        [InlineKeyboardButton(text="◀️ Back", callback_data=MenuCallback.MAIN)]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def material_actions_keyboard(material_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Summary",
                    callback_data=f"{MaterialCallback.SUMMARY_PREFIX}{material_id}",
                ),
                InlineKeyboardButton(
                    text="🃏 Flashcards",
                    callback_data=f"{MaterialCallback.FLASHCARD_PREFIX}{material_id}:0:q",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❓ Quiz",
                    callback_data=f"{QuizCallback.START_PREFIX}{material_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Back", callback_data=MenuCallback.MATERIALS
                )
            ],
        ]
    )


def flashcard_keyboard(
    material_id: str, index: int, total: int, show_answer: bool
) -> InlineKeyboardMarkup:
    nav: list[InlineKeyboardButton] = []
    prefix = MaterialCallback.FLASHCARD_PREFIX
    if index > 0:
        nav.append(
            InlineKeyboardButton(
                text="⬅️ Prev",
                callback_data=f"{prefix}{material_id}:{index - 1}:{'a' if show_answer else 'q'}",
            )
        )
    toggle = "a" if show_answer else "q"
    nav.append(
        InlineKeyboardButton(
            text="👁 Show Answer" if not show_answer else "❓ Show Question",
            callback_data=f"{prefix}{material_id}:{index}:{toggle}",
        )
    )
    if index < total - 1:
        nav.append(
            InlineKeyboardButton(
                text="Next ➡️",
                callback_data=f"{prefix}{material_id}:{index + 1}:{'a' if show_answer else 'q'}",
            )
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav,
            [
                InlineKeyboardButton(
                    text="◀️ Back",
                    callback_data=f"{MaterialCallback.PREFIX}{material_id}",
                )
            ],
        ]
    )


def flashcards_materials_keyboard(materials: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=title[:40],
                callback_data=f"{MaterialCallback.FLASHCARD_PREFIX}{mid}:0:q",
            )
        ]
        for mid, title in materials
    ]
    rows.append(
        [InlineKeyboardButton(text="◀️ Back", callback_data=MenuCallback.MAIN)]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_materials_keyboard(materials: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=title[:40],
                callback_data=f"{QuizCallback.START_PREFIX}{mid}",
            )
        ]
        for mid, title in materials
    ]
    rows.append(
        [InlineKeyboardButton(text="◀️ Back", callback_data=MenuCallback.MAIN)]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_answer_keyboard(
    material_id: str, question_index: int, options: list[str]
) -> InlineKeyboardMarkup:
    labels = ["A", "B", "C", "D", "E", "F"]
    rows = []
    for i, option in enumerate(options):
        label = labels[i] if i < len(labels) else str(i + 1)
        text = f"{label}. {option[:50]}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"{QuizCallback.ANSWER_PREFIX}{material_id}:{question_index}:{i}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
