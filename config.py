
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-chat-v3-0324:free",
)

USERS_JSON = DATA_DIR / "users.json"
CACHE_JSON = DATA_DIR / "ai_cache.json"
LEADERBOARD_JSON = DATA_DIR / "leaderboard.json"

MAX_FILE_SIZE_MB = 20
MAX_TEXT_LENGTH = 30_000
FLASHCARD_COUNT = 5
QUIZ_QUESTION_COUNT = 5

OPENROUTER_MAX_TOKENS = 1500
MAX_AI_INPUT_CHARS = 6_000
MAX_CHUNK_CHARS = 2_000
MAX_SUMMARY_CHARS = 500

SUPPORTED_EXTENSIONS = {".pdf", ".pptx", ".ppt", ".txt"}
