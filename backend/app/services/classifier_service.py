"""
Very simple keyword–rule classifier.
Replace with a ML model later by loading a pickle instead of KEYWORDS dict.
"""

import re
from functools import lru_cache
from typing import Dict

KEYWORDS: Dict[str, list[str]] = {
    "bonus":  [r"\bbonus", r"\bfreespin", r"cashback"],
    "deposit": [r"\bdeposit", r"\bdepo", r"\btop[\s-]?up", r"\badd(ed)? funds?"],
    "withdraw": [r"\bwithdra?w", r"\bcashout", r"\bpayout"],
    "login":   [r"\blog[\w\s]*in\b", r"\baccess issues?", r"\b2fa", r"\bpassword"],
    "angry":   [r"\bsucks?", r"\b(sc|f)am", r"\bwtf", r"\bangry", r"\bmad"],
}

DEFAULT = "other"


@lru_cache()
def _compiled():
    return {c: [re.compile(pat, re.I) for pat in pats] for c, pats in KEYWORDS.items()}


def classify(text: str) -> str:
    for category, patterns in _compiled().items():
        if any(p.search(text) for p in patterns):
            return category
    return DEFAULT
