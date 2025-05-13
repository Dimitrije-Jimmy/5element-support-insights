"""Stats helpers that talk to Supabase."""

from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
from supabase import create_client
from .config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def fetch_messages(
    category: str | None,
    source: str | None,
    start: datetime | None,
    end: datetime | None,
) -> pd.DataFrame:
    query = supabase.table("messages").select("*")
    if category:
        query = query.eq("category", category)
    if source:
        query = query.eq("source", source)
    if start:
        query = query.gte("timestamp", start.isoformat())
    if end:
        query = query.lte("timestamp", end.isoformat())

    data = query.execute().data  # type: ignore
    return pd.DataFrame(data)


def basic_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"messages": 0, "unique_users": 0}
    return {
        "messages": len(df),
        "unique_users": df["id_user"].nunique(),
    }



def spike_dates(df: pd.DataFrame, threshold: int = 3) -> List[Tuple[str, int]]:
    """Return dates where count > mean + threshold*std."""
    if df.empty:
        return []

    daily = df.groupby(df["timestamp"].str[:10]).size()
    mean, std = daily.mean(), daily.std()
    spikes = daily[daily > mean + threshold * std]
    return list(spikes.items())
