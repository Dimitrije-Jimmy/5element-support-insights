"""
Chat endpoint: accepts natural-language queries,
asks the LLM to extract filters via function-calling,
runs stats, and replies in friendly prose while
remembering previous filters.

Works with:
* OpenAI / Gemini services (they forward the tools schema)
* HF fallback (tools ignored, regex fallback used)
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends

from ....models import ChatRequest, ChatResponse
from ....reports import basic_metrics, fetch_messages, spike_dates
from ....services import LLMServiceProtocol, get_llm_service

router = APIRouter()

# ────────────────────────
#  Conversational memory
# ────────────────────────
_memory: Dict[str, Dict[str, Any]] = {}  # keyed by user-id


def _remember(user_id: str, category, source, days):
    _memory[user_id] = {"category": category, "source": source, "days": days}

def _dt_iso(x):
    return x if isinstance(x, str) else x.isoformat(timespec="seconds")

# ────────────────────────
#  LLM tool schema (aka function spec)
# ────────────────────────
FILTER_SCHEMA = {
    "name": "filter_messages",
    "description": "Extract filters from the user query",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": [
                    "bonus",
                    "deposit",
                    "withdraw",
                    "game_issue",
                    "login_account",
                    "anger_feedback",
                    "other",
                ],
            },
            "source": {
                "type": "string",
                "enum": ["livechat", "telegram"],
            },
            "days_back": {
                "type": "integer",
                "description": "Look-back window in days",
            },
        },
    },
}

# ────────────────────────
#  Fallback regex parser (HF models ignore tool schema)
# ────────────────────────
_CAT_RE = re.compile(
    r"\b(bonus|deposit|withdraw|game\w*|login|angry|anger)\b", re.I
)
_SRC_RE = re.compile(r"\b(livechat|telegram)\b", re.I)
_DAYS_RE = re.compile(r"\b(\d+)\s*day", re.I)


def _regex_parse(text: str) -> Tuple[Optional[str], Optional[str], int]:
    cat = _CAT_RE.search(text)
    src = _SRC_RE.search(text)
    days = _DAYS_RE.search(text)
    return (
        cat.group(1).lower() if cat else None,
        src.group(1).lower() if src else None,
        int(days.group(1)) if days else 30,
    )


# ────────────────────────
#  Endpoint
# ────────────────────────
@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    svc: LLMServiceProtocol = Depends(get_llm_service),
):
    user_id = "demo"  # replace with auth-derived id in prod

    # ---------- 1) call LLM with function schema ----------
    llm_raw = await svc.chat(
        prompt=req.message,
        history=req.history,
        tools=[FILTER_SCHEMA],
    )

    # ---------- 2) extract filters ----------
    category = source = None
    days = 30

    if isinstance(llm_raw, dict) and llm_raw.get("tool_call"):
        try:
            args = json.loads(llm_raw["tool_call"]["arguments"])
            category = args.get("category")
            source = args.get("source")
            days = args.get("days_back", 30)
        except Exception:
            # fall back if JSON malformed
            pass

    if category is None and source is None:
        # we’re on HF local model → use regex
        category, source, days = _regex_parse(req.message)

    # ---------- 3) merge with memory ----------
    mem = _memory.get(user_id, {})
    category = category or mem.get("category")
    source = source or mem.get("source")
    days = days or mem.get("days", 30)
    _remember(user_id, category, source, days)

    # ---------- 4) fetch stats ----------
    end = _dt.datetime.utcnow()
    start = end - _dt.timedelta(days=days)
    df = fetch_messages(category, source, _dt_iso(start), _dt_iso(end))
    stats = basic_metrics(df)
    spikes = spike_dates(df)

    # ---------- 5) craft human reply ----------
    parts = [
        f"In the last **{days} days**",
        f"we recorded **{stats['messages']} messages**",
        f"from **{stats['unique_users']} users**",
    ]
    if category:
        parts.append(f"about **{category.replace('_', ' ')}**")
    if source:
        parts.append(f"via **{source.capitalize()}**")
    answer = ", ".join(parts) + "."

    if spikes:
        date, count = spikes[-1]
        answer += f" Notably, {count} on {date}."

    return ChatResponse(answer=answer)
