# AI Study Assistant — Telegram Bot

Production-ready Telegram bot for a university final project. Upload study materials (PDF, PPTX, TXT), paste text, or send links — the bot uses **OpenRouter** (DeepSeek free model) to generate summaries, flashcards, and interactive quizzes. All data is stored locally in **JSON** (no database).

## Features

- Extract text from **PDF**, **PPTX**, and **TXT**
- AI-generated **summary**, **5 flashcards**, and **5 multiple-choice quiz** questions
- **My Materials** — review saved content
- **Flashcards** viewer with prev/next and show-answer buttons
- **Interactive quiz** with inline buttons and scoring
- **User profile** — score, material count, daily streak
- **Leaderboard** and **daily motivation** (bonus)
- **AI response caching** to reduce API calls

## Architecture

```
finalitpTGBOT/
├── bot.py                 # Entry point
├── config.py              # Environment & paths
├── handlers/              # Telegram handlers (aiogram 3)
├── services/              # Business logic
├── models/                # OOP domain models (User, Material, Quiz)
├── parsers/               # BaseParser + PDF/PPTX/TXT (inheritance)
├── ai/                    # OpenRouter API + response parser
├── storage/               # JSON persistence
├── keyboards/             # Reply & inline keyboards
└── data/                  # users.json, ai_cache.json (auto-created)
```

### OOP highlights

- **Inheritance**: `BaseParser` → `PDFParser`, `PPTXParser`, `TXTParser`
- **Polymorphism**: `ParserFactory.extract_text()` calls `parser.extract()` on the correct subclass
- **Domain classes**: `User`, `Material`, `Quiz`, `QuizSession`, `AIService`

## Requirements

- Python 3.10+
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- OpenRouter API key ([OpenRouter](https://openrouter.ai/keys))

## Setup

1. **Clone or copy** the project folder.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

   Windows:

   ```powershell
   .\venv\Scripts\activate
   ```

   Linux/macOS:

   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:

   ```bash
   copy .env.example .env
   ```

   Edit `.env` and set:

   - `BOT_TOKEN` — from BotFather
   - `OPENROUTER_API_KEY` — from OpenRouter

5. **Run the bot**:

   ```bash
   python bot.py
   ```

## Usage

| Action | How |
|--------|-----|
| Start | `/start` or open the bot |
| Upload file | Send PDF / PPTX / TXT as a **document** |
| Paste notes | Send a text message |
| Link (optional) | Send a URL (short message with link) |
| My Materials | Reply button or inline menu |
| Flashcards | Material → Flashcards → navigate with buttons |
| Quiz | **Start Quiz** → pick material → answer with inline buttons |
| Profile | View score, materials count, streak |
| Leaderboard | Top users by score |
| Motivation | Daily motivational message |

## Data storage

`data/users.json` structure:

```json
{
  "123456789": {
    "username": "student",
    "first_name": "Alex",
    "score": 50,
    "streak": 3,
    "last_active": "2026-05-21",
    "materials": [
      {
        "id": "a1b2c3d4",
        "title": "Lecture Notes",
        "summary": "...",
        "flashcards": [{"question": "...", "answer": "..."}],
        "quiz": [
          {
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "correct_index": 0
          }
        ]
      }
    ]
  }
}
```

Corrupt JSON files are backed up automatically and reset to `{}`.

## Error handling

- Invalid file types or empty documents
- OpenRouter API failures, rate limits, and empty AI responses
- JSON corruption with backup recovery
- Global dispatcher error handler — bot keeps running

## Project notes (final submission)

- **Stack**: Python, aiogram 3, OpenRouter (requests), JSON storage
- **No SQL database** — per assignment requirements
- **Async**: aiogram polling, `asyncio.to_thread` for sync OpenRouter/pdf calls

## License

Educational use — university final project.
