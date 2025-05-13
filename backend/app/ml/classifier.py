from functools import lru_cache
from typing import List
from .prompts import SYSTEM_PROMPT, CATEGORIES
from ..config import settings

# Option A: OpenAI (zero‑shot) -------------------------------------------------

def classify_openai(msg: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": msg}],
        max_tokens=4,
    )
    label = completion.choices[0].message.content.strip().lower()
    return label if label in CATEGORIES else "general_feedback"

# Option B: HF text‑classification model ---------------------------------------

@lru_cache()
def _hf_pipeline():
    from transformers import pipeline
    return pipeline("text-classification", model=settings.HF_MODEL, truncation=True)

def classify_hf(msg: str) -> str:
    classifier = _hf_pipeline()
    res = classifier(msg)[0]
    # naïve mapping – adapt to your fine‑tuned labels
    return "general_feedback" if res["score"] < 0.5 else res["label"].lower()

# Unified entrypoint -----------------------------------------------------------

def classify(msg: str) -> str:
    if settings.OPENAI_API_KEY:
        return classify_openai(msg)
    return classify_hf(msg)