"""Central callback_data values — must match handler filters exactly."""


class MenuCallback:
    MAIN = "menu:main"
    MATERIALS = "menu:materials"
    QUIZ = "menu:quiz"
    FLASHCARDS = "menu:flashcards"
    PROFILE = "menu:profile"
    LEADERBOARD = "menu:leaderboard"
    SCHEDULE = "menu:schedule"
    MOTIVATION = "menu:motivation"


class MaterialCallback:
    PREFIX = "mat:"
    SUMMARY_PREFIX = "sum:"
    FLASHCARD_PREFIX = "fc:"


class QuizCallback:
    MENU = MenuCallback.QUIZ
    START_PREFIX = "quiz_start:"
    ANSWER_PREFIX = "quiz_ans:"
