"""message_classifier_service.py

A self‑contained script that:
1. Extracts 5–6 actionable categories from a free‑form dataset of user messages.
2. Classifies every message into one of those categories (or `Irrelevant/Other`).
3. Writes the results back to a CSV next to the original file.

The script first asks the LLM (OpenAI GPT‑4o by default) to synthesize good
categories from a representative sample of messages.  It then streams the
messages through the model in batches and labels them.  The prompts are
grounded, deterministic and cost‑aware, and the script automatically falls
back to a lightweight keyword classifier if no API key is available.

Usage
-----
$ export OPENAI_API_KEY=sk‑...
$ python message_classifier_service.py /path/to/messages.csv

Dependencies
------------
pip install pandas tqdm openai tiktoken nest_asyncio
"""

from __future__ import annotations
import os
import sys
import json, re
import random
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict
from pydantic import Field

import pandas as pd
from tqdm.auto import tqdm

try:
    import openai
except ImportError:
    openai = None  # allow keyword fallback


# ==== Prompt Templates ======================================================

SYSTEM_CATEGORISE = """You are to respond **only** with a valid json array
You are a senior customer‑support analyst.
Analyse the user messages below and propose **exactly seven** broad,
actionable issue categories that an operator could route to different
internal teams.  Each category must be:
• Distinct (no overlap)
• Action‑oriented (e.g. “Deposit / Payment Issues”)
• Relevant to multiple messages
Return a JSON array of objects:
[{\"name\": <short label>, \"description\": <1‑sentence description>}, …]"""

SYSTEM_LABEL = """You are a classifier that assigns user messages to
one of the support categories provided.  If NONE apply, respond with
“Irrelevant/Other”.  Respond with the **category name only** – no extra
text.
Please return just the label as json string."""


# ==== LLM Utilities =========================================================

def _strip_md_fences(txt: str) -> str:
    """
    Remove triple-back-tick code fences and leading language tags, then trim.
    Keeps the inner JSON unchanged.
    """
    txt = re.sub(r"^\s*```(?:json)?\s*|\s*```?\s*$", "", txt, flags=re.IGNORECASE | re.DOTALL)
    return txt.strip()

async def get_openai_completion(system: str, user: str, model: str = "gpt-4o-mini") -> str:
    """Return the assistant's content as a string, working with both
    openai<1.0 (ChatCompletion) and ≥1.0 (chat.completions.create)."""
    if openai is None:
        raise RuntimeError("openai package not installed")
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_API_KEY="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"
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    
    # === New style (>=1.0) --------------------------------------------------
    if hasattr(openai, "AsyncOpenAI"):
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        kwargs = dict(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
        )

        try:
            # first try with explicit JSON request
            response = await client.chat.completions.create(
                **kwargs, response_format={"type": "json_object"}
            )
        except openai.BadRequestError as e:
            if "must contain the word 'json'" in str(e).lower():
                # retry without forcing json_object
                response = await client.chat.completions.create(**kwargs)
            else:
                raise
        return response.choices[0].message.content.strip()

    # === Legacy style (<1.0) ------------------------------------------------
    openai.api_key = OPENAI_API_KEY
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
        # ask for raw JSON if the model supports it (ignored otherwise)
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


# ==== Category Discovery ====================================================

async def discover_categories(messages: List[str], sample_size: int = 400) -> List[Dict]:
    sample = random.sample(messages, min(sample_size, len(messages)))
    user_prompt = "\n".join(sample)
    raw = await get_openai_completion(SYSTEM_CATEGORISE, user_prompt)
    try:
        data = json.loads(_strip_md_fences(raw))
        #assert isinstance(data, list) and len(data) == 7

        # Accept either a bare list  or  an object holding the list.
        if isinstance(data, list):
            categories = data
        elif isinstance(data, dict) and data:
            # take the *first* field that looks like a list of dicts
            first_val = next(iter(data.values()))
            if isinstance(first_val, list):
                categories = first_val
            else:
                raise ValueError("No list found in JSON object")
        else:
            raise ValueError("Unexpected JSON structure")

        # make sure it’s a list of dicts with a “name” key    
        for c in categories:
            #assert "name" in c and "description" in c
            if not isinstance(c, dict) or "name" not in c:
                raise ValueError("Malformed category entry")
        return categories
    except Exception:
        raise ValueError(f"Invalid JSON from model:\n{raw}")


# ==== Classification ========================================================

async def label_messages(messages: List[str], categories: List[Dict], batch_size: int = 50) -> List[str]:
    category_text = json.dumps([c["name"] for c in categories])
    labels: List[str] = []

    for i in tqdm(range(0, len(messages), batch_size), desc="LLM classify"):
        batch = messages[i:i+batch_size]
        tasks = [get_openai_completion(
                    SYSTEM_LABEL + f"\n\nCategories: {category_text}",
                    msg)
                 for msg in batch]
        batch_labels = await asyncio.gather(*tasks)
        labels.extend([_strip_md_fences(p).strip(' "\'') for p in batch_labels])
    return labels


# ==== Fallback Keyword Classifier ===========================================

KEYWORD_CATS = {
    "Account/Login Issues": ["login", "account", "password", "verify", "kyc", "access"],
    "Deposit/Payment Issues": ["deposit", "payment", "credit card", "fund", "add money"],
    "Withdrawal/Cashout Issues": ["withdraw", "cashout", "payout", "transfer"],
    "Bonuses/Promotions Issues": ["bonus", "free spins", "promotion", "cashback", "offer"],
    "Gameplay/Technical Issues": ["game", "crash", "error", "bug", "spin", "loading"],
}

def keyword_label(msg: str) -> str:
    m = msg.lower()
    for cat, kws in KEYWORD_CATS.items():
        if any(kw in m for kw in kws):
            return cat
    return "Irrelevant/Other"


# ==== Main ==================================================================

async def main(path: str):
    df = pd.read_csv(path)
    if "message" not in df.columns:
        raise ValueError("CSV must have a 'message' column")

    msgs = df["message"].astype(str).tolist()

    # Try LLM route; fallback to keywords
    try:
        categories = await discover_categories(msgs)
        labels = await label_messages(msgs, categories)
    except Exception as e:
        print(f"[Warning] Falling back to keyword classifier: {e}")
        categories = [{"name": k, "description": "auto‑keyword"} for k in KEYWORD_CATS]
        labels = [keyword_label(m) for m in tqdm(msgs, desc="Keyword classify")]

    df["category"] = labels
    out_path = str(Path(path)) + "_labelled.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    # Show quick summary
    print(df["category"].value_counts())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify support messages.")
    parser.add_argument("dataset", help="CSV file with a 'message' column")
    args = parser.parse_args()
    asyncio.run(main(args.dataset))
