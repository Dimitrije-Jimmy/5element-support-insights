from functools import lru_cache
from typing import List
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

# Original categories from the trained model
LABELS = ["bonus", "deposit", "withdraw", "game_issue", "login_account", "anger_feedback", "other"]

@lru_cache()
def _load():
    tok = AutoTokenizer.from_pretrained("distilbert-classifier-saved")
    mdl = AutoModelForSequenceClassification.from_pretrained("distilbert-classifier-saved", num_labels=len(LABELS))
    mdl.eval()
    return tok, mdl

def classify(text: str) -> str:
    tok, mdl = _load()
    with torch.no_grad():
        inputs = tok(text, return_tensors="pt", truncation=True)
        logits = mdl(**inputs).logits
        cat = logits.argmax(-1).item()
    return LABELS[cat]

def get_probabilities(text: str) -> dict:
    tok, mdl = _load()
    with torch.no_grad():
        inputs = tok(text, return_tensors="pt", truncation=True)
        logits = mdl(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
    return {label: float(prob) for label, prob in zip(LABELS, probs)}
