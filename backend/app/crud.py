from typing import List
from datetime import datetime
from supabase import Client
from .schemas import MessageIn, QueryFilters

TABLE = "messages"

# Insert

def insert_messages(db: Client, rows: List[dict]):
    db.table(TABLE).insert(rows).execute()

# Query with optional filters

def fetch_messages(db: Client, f: QueryFilters):
    q = db.table(TABLE).select("*")
    if f.category:
        q = q.eq("category", f.category)
    if f.source:
        q = q.eq("source", f.source)
    if f.start_date:
        q = q.gte("timestamp", f.start_date.isoformat())
    if f.end_date:
        q = q.lte("timestamp", f.end_date.isoformat())
    return q.execute().data

# Aggregates

def count_messages(db: Client, f: QueryFilters):
    q = db.rpc("count_messages", params={"category": f.category, "source": f.source, "start": f.start_date, "end": f.end_date})
    return q.execute().data[0]["count"]