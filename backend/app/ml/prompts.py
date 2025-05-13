CATEGORIES = [
    "login_issues",
    "deposit_issues",
    "bonus_questions",
    "geo_restriction",
    "general_feedback",
]

SYSTEM_PROMPT = (
    "You are a support classifier.  Map each user message into exactly one of these categories: "
    + ", ".join(CATEGORIES)
    + ". If none apply, return 'general_feedback'.  Return the raw label only."
)