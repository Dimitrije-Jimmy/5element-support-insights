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
        # Handle multiple categories
        categories = category.split(',') if ',' in category else [category]
        if len(categories) == 1:
            query = query.eq("category", categories[0])
        else:
            query = query.in_("category", categories)
    if source:
        query = query.eq("source", source)
    if start:
        query = query.gte("timestamp", start.isoformat())
    if end:
        query = query.lte("timestamp", end.isoformat())

    data = query.execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def basic_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "total_messages": 0,
            "unique_users": 0,
            "categories": {}
        }
    
    category_counts = df.groupby('category').size().to_dict()
    
    return {
        "total_messages": len(df),
        "unique_users": df["id_user"].nunique(),
        "categories": category_counts
    }


def spike_dates(df: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
    """Return dates where count > mean + threshold*std."""
    if df.empty:
        return []

    # Group by date and count messages
    daily = df.groupby(df['timestamp'].dt.date).size()
    
    if len(daily) < 2:  # Need at least 2 points for std
        return []

    mean, std = daily.mean(), daily.std()
    spikes = daily[daily > mean + threshold * std]
    
    return [
        {
            "date": date.strftime("%Y-%m-%d"),
            "count": int(count),
            "message": f"Spike of {int(count)} messages (vs avg {int(mean)})"
        }
        for date, count in spikes.items()
    ]
