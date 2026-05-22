"""Handler routers — registration is done in main.register_routers()."""

from handlers.callbacks import router as callbacks_fallback_router
from handlers.documents import router as documents_router
from handlers.materials import router as materials_router
from handlers.menu import router as menu_router
from handlers.profile import router as profile_router
from handlers.quiz import router as quiz_router
from handlers.reply_menu import router as reply_menu_router
from handlers.start import router as start_router
from handlers.text import router as text_router

__all__ = [
    "start_router",
    "reply_menu_router",
    "documents_router",
    "materials_router",
    "quiz_router",
    "profile_router",
    "menu_router",
    "text_router",
    "callbacks_fallback_router",
]


def register_routers(dp) -> None:
    dp.include_router(start_router)
    dp.include_router(reply_menu_router)
    dp.include_router(documents_router)
    dp.include_router(materials_router)
    dp.include_router(quiz_router)
    dp.include_router(profile_router)
    dp.include_router(menu_router)
    dp.include_router(text_router)
    dp.include_router(callbacks_fallback_router)
