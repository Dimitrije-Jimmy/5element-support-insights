#!/usr/bin/env python
"""Bulk‑load the provided CSV into Supabase via the `messages` table."""
import csv
import argparse
from datetime import datetime
from pathlib import Path
from supabase import create_client
from app.config import settings

DATE_FMT = "%m/%d/%Y"  # matches the sample rows


def parse_ts(date_str: str) -> str:
    return datetime.strptime(date_str, DATE_FMT).isoformat()

def main(csv_path: Path):
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    rows = []
    with csv_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            r["timestamp"] = parse_ts(r["timestamp"])
            r["category"] = None
            rows.append(r)

    CHUNK = 500
    for i in range(0, len(rows), CHUNK):
        _ = client.table("messages").insert(rows[i : i + CHUNK]).execute()
    print(f"✅ Inserted {len(rows)} rows → Supabase")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    main(p.parse_args().csv)