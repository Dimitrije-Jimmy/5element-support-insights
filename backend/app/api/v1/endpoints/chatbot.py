"""
Chat endpoint: accepts natural-language queries about message statistics
and responds with insights about user issues.

Works with:
* OpenAI / Gemini services (they forward the tools schema)
* HF fallback (tools ignored, regex fallback used)
"""

from __future__ import annotations

import datetime as _dt
from datetime import datetime
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends

from ....models import ChatRequest, ChatResponse
from ....reports import basic_metrics, fetch_messages, spike_dates
from ....services import LLMServiceProtocol, get_llm_service

router = APIRouter()

# Dataset date range
DATASET_START = datetime(2024, 1, 11)  # January 11, 2024
DATASET_END = datetime(2025, 1, 30)    # January 30, 2025

# ────────────────────────
#  Conversational memory
# ────────────────────────
_memory: Dict[str, Dict[str, Any]] = {}  # keyed by user-id


def _remember(user_id: str, category, source, days):
    _memory[user_id] = {"category": category, "source": source, "days": days}

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
                "maximum": 365  # Allow up to a year
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

def _format_category(cat: str) -> str:
    """Make category name more readable"""
    if not cat:
        return "all categories"
    return cat.replace("_", " ")

def _format_source(src: str) -> str:
    """Format source name"""
    if not src:
        return "all channels"
    return src.capitalize()

def _format_time_range(days: int) -> str:
    """Format time range in natural language"""
    if days == 1:
        return "today"
    elif days == 7:
        return "this week"
    elif days == 30:
        return "this month"
    return f"last {days} days"

def _format_response(stats: Dict[str, Any], category: str, source: str, days: int, spikes: List) -> str:
    """Create a natural language response about the statistics"""
    parts = []
    
    # Basic stats
    time_range = _format_time_range(days)
    cat_name = _format_category(category)
    src_name = _format_source(source)
    
    msg_count = stats.get('total_messages', 0)
    user_count = stats.get('unique_users', 0)
    
    if msg_count == 0:
        return f"I found no messages about {cat_name} via {src_name} in the {time_range}."
    
    parts.append(f"In the {time_range}, ")
    
    if category and source:
        parts.append(f"there were **{msg_count} {cat_name} issues** reported via {src_name}")
    elif category:
        parts.append(f"there were **{msg_count} {cat_name} issues** reported across all channels")
    elif source:
        parts.append(f"**{msg_count} issues** were reported via {src_name}")
    else:
        parts.append(f"there were **{msg_count} issues** reported across all channels")
    
    parts.append(f" by **{user_count} unique users**")
    
    # Add spike information if available
    if spikes:
        latest_spike = spikes[-1]
        parts.append(f". There was a notable spike of **{latest_spike['count']} messages** on {latest_spike['date']}")
    
    return "".join(parts) + "."

# ────────────────────────
#  Endpoint
# ────────────────────────
@router.post("")
async def chat(
    req: ChatRequest,
    svc: LLMServiceProtocol = Depends(get_llm_service),
):
    user_id = "demo"  # replace with auth-derived id in prod

    # ---------- 1) Extract filters with LLM ----------
    filter_response = await svc.chat(
        prompt=f"""Extract date range and filters from: "{req.message}"
Note: Our dataset only contains support messages from {DATASET_START.strftime('%B %d, %Y')} to {DATASET_END.strftime('%B %d, %Y')}.""",
        history=[msg.content for msg in req.history],
        tools=[FILTER_SCHEMA],
    )

    # ---------- 2) Parse filters ----------
    category = source = None
    days = 30  # Default to last 30 days

    if isinstance(filter_response, dict) and filter_response.get("tool_call"):
        try:
            args = json.loads(filter_response["tool_call"]["arguments"])
            category = args.get("category")
            source = args.get("source")
            days = min(args.get("days_back", 30), 365)  # Cap at 1 year
        except Exception:
            pass

    # ---------- 3) fetch data and analyze ----------
    end = min(DATASET_END, _dt.datetime.utcnow())
    start = max(DATASET_START, end - _dt.timedelta(days=days))
    df = fetch_messages(category, source, start, end)
    
    # Validate we have data
    if df.empty:
        return ChatResponse(
            response=f"I found no support messages for your query in our dataset (which covers {DATASET_START.strftime('%B %d, %Y')} to {DATASET_END.strftime('%B %d, %Y')}).",
            context=f"No data found between {start.date()} and {end.date()}"
        )

    stats = basic_metrics(df)
    spikes = spike_dates(df)

    # Get actual date range from data
    actual_start = df['timestamp'].min()
    actual_end = df['timestamp'].max()
    
    # Get category breakdown if any messages found
    category_counts = {}
    if not df.empty:
        category_counts = df.groupby('category').size().to_dict()

    # ---------- 4) Generate contextual response ----------
    prompt = f"""You are a support analytics assistant. Answer the following query concisely in 1-2 sentences: "{req.message}"

Available data range: {DATASET_START.strftime('%B %d, %Y')} to {DATASET_END.strftime('%B %d, %Y')}
Current query period: {actual_start.strftime('%B %d, %Y')} to {actual_end.strftime('%B %d, %Y')}

Facts:
- Total messages: {stats['total_messages']}
- By category: {category_counts}
- Unique users: {stats['unique_users']}
{f"- Spike detected: {spikes[-1]['count']} messages on {spikes[-1]['date']}" if spikes else ""}

Rules:
1. Only report numbers that are explicitly shown in the facts above
2. If asked about dates outside our data range, mention the actual data range
3. Never make up or estimate numbers
4. If unsure, say you don't have that specific information"""

    response = await svc.chat(prompt=prompt, history=[msg.content for msg in req.history])
    
    if isinstance(response, dict):
        response = response.get("content", "I couldn't analyze the support data properly.")

    return ChatResponse(
        response=response,
        context=f"Found {stats['total_messages']} messages from {actual_start.strftime('%B %d')} to {actual_end.strftime('%B %d, %Y')}"
    )
