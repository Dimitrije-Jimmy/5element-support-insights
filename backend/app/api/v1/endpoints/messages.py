from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Query
#from ....services.classifier_service import classify
from ....services.bert_classifier import classify

from ....models import Message
from .... import reports  # new helper

import csv, pathlib, datetime
CSV_PATH = pathlib.Path("data/messages_mirror.csv")

router = APIRouter()

@router.post("/", response_model=Message)
async def ingest(msg: Message):
    if msg.category is None:
        msg.category = classify(msg.message)
    # insert into Supabase
    _ = reports.supabase.table("messages").insert(msg.dict()).execute()

    # local CSV upsert (append)
    write_header = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=msg.dict().keys())
        if write_header: w.writeheader()
        w.writerow(msg.dict())

    return msg

@router.get("/metrics")
async def metrics(
    category: Annotated[Optional[str], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    start: Annotated[Optional[str], Query()] = None,
    end: Annotated[Optional[str], Query()] = None,
):
    dt_start = datetime.fromisoformat(start) if start else None
    dt_end   = datetime.fromisoformat(end)   if end   else None
    df = reports.fetch_messages(category, source, dt_start, dt_end)
    return {
        **reports.basic_metrics(df),
        "spikes": reports.spike_dates(df),
    }

@router.post("/classify")
def classify_snippet(text: str):
    return {"category": classify(text)}

