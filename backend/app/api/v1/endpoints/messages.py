from datetime import datetime as dt
from typing import Annotated, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Query
#from ....services.classifier_service import classify
from ....services.bert_classifier import classify

from ....models import Message
from .... import reports  # new helper

import csv, pathlib, datetime
CSV_PATH = pathlib.Path("data/messages_mirror.csv")

router = APIRouter()

class ClassifyRequest(BaseModel):
    message: str

def parse_date(date_str: Optional[str]) -> Optional[dt]:
    if not date_str:
        return None
    try:
        return dt.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

@router.post("")
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
    dt_start = parse_date(start)
    dt_end = parse_date(end)
    df = reports.fetch_messages(category, source, dt_start, dt_end)
    return {
        **reports.basic_metrics(df),
        "spikes": reports.spike_dates(df),
    }

@router.post("/classify")
async def classify_snippet(request: ClassifyRequest):
    return {"category": classify(request.message)}

@router.get("/categories")
async def get_categories():
    """Return list of unique categories from the database."""
    query = reports.supabase.table("messages").select("category").execute()
    categories = set(row["category"] for row in query.data if row["category"])
    return sorted(list(categories))

