"""
AI Study Assistant — Telegram Bot entry point (legacy).

Run: python main.py  (preferred)
     python bot.py   (delegates to main)
"""

from __future__ import annotations

import asyncio
import logging
import sys
from main import main, on_error, register_routers, validate_config

__all__ = ["main", "on_error", "register_routers", "validate_config"]

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Bot stopped.")
