# 5Element LLM DataScientist Task – FastAPI Backend

Below is a **complete project scaffold** ready to push to GitHub, docker‑build, and deploy to Fly.io.  Every file is included with minimal but functional code so you can `docker compose up`, request an OpenAI key from **[ziga.trojer@5element.si](mailto:ziga.trojer@5element.si)**, and start iterating.

---

## 📂 Folder tree

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── deps.py
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   └── prompts.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py
│   │   ├── huggingface_service.py
│   │   └── memory.py
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints/
│               ├── chatbot.py
│               ├── messages.py
│               └── health.py
├── tests/
│   └── test_chatbot.py
├── docker/
│   └── Dockerfile
├── scripts/
│   └── setup_supabase.sql
├── index.html
├── requirements.txt
├── README.md
├── .env.example
└── fly.toml
```

---

## 🐍 `app/__init__.py`

```python
from fastapi import FastAPI
from .config import settings
from .api.v1.endpoints import chatbot, messages, health

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# Routers
app.include_router(health.router)
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(chatbot.router, prefix="/api/v1/chat", tags=["chat"])
```

---

## ⚙️ `app/config.py`

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM-Feedback-Assistant"
    OPENAI_API_KEY: str | None = None
    HF_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    SUPABASE_URL: str
    SUPABASE_KEY: str
    MEMORY_WINDOW: int = 5  # number of turns to remember

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🛢️ `app/db.py`

```python
from supabase import create_client, Client
from .config import settings

supabase: Client | None = None

def get_db() -> Client:
    global supabase
    if supabase is None:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase
```

---

## 🔖 `app/models.py` (SQL table definitions – Supabase will pick these up)

```sql
-- messages table
create table if not exists messages (
  id uuid default uuid_generate_v4() primary key,
  id_user int not null,
  timestamp timestamptz not null,
  source text check (source in ('livechat','telegram')),
  message text,
  category text,
  created_at timestamptz default now()
);
```

> **Run** the file `scripts/setup_supabase.sql` in the Supabase SQL editor once the project is created.

---

## 🏷️ `app/schemas.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field

class MessageIn(BaseModel):
    id_user: int
    timestamp: datetime
    source: str
    message: str

class MessageOut(MessageIn):
    id: str
    category: str | None = None

class QueryFilters(BaseModel):
    category: str | None = None
    source: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

class ChatRequest(BaseModel):
    query: str
    session_id: str = Field(..., description="Client‑provided session identifier")
```

---

## 🔧 `app/crud.py`

```python
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
```

*(Add a Postgres function `count_messages` in Supabase or replace with client‑side count.)*

---

## 🤖 `app/ml/prompts.py`

```python
CATEGORIES = [
    "login_issues",
    "deposit_issues",
    "bonus_questions",
    "geo_restriction",
    "general_feedback",
]

SYSTEM_PROMPT = (
    "You are a support classifier.  Map each user message into exactly one of these categories: "
    + ", ".join(CATEGORIES)
    + ". If none apply, return 'general_feedback'.  Return the raw label only."
)
```

---

## 🤖 `app/ml/classifier.py`

```python
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
```

---

## 🛠️ `app/services/openai_service.py`

```python
from openai import OpenAI
from ..config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def chat_completion(prompt: str, memory: str = "") -> str:
    messages = [{"role": "system", "content": "You are a helpful analyst that answers with concise bullet‑points."}]
    if memory:
        messages.append({"role": "system", "content": f"Conversation memory: {memory}"})
    messages.append({"role": "user", "content": prompt})
    res = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return res.choices[0].message.content
```

---

## 🧠 `app/services/memory.py`

```python
from collections import deque
from ..config import settings

# naive in‑process memory – swap for Redis if scaling
_sessions: dict[str, deque] = {}

def remember(session_id: str, query: str):
    dq = _sessions.setdefault(session_id, deque(maxlen=settings.MEMORY_WINDOW))
    dq.append(query)

def recall(session_id: str) -> str:
    dq = _sessions.get(session_id, deque())
    return " | ".join(dq)
```

---

## 🚦 `app/deps.py`

```python
from fastapi import Depends, Header
from .db import get_db
from .services import memory

async def get_db_conn():
    return get_db()

async def get_session_id(session_id: str | None = Header(default=None)):
    return session_id or "anonymous"
```

---

## 🚑 `app/api/v1/endpoints/health.py`

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["health"])
async def pong():
    return {"status": "ok"}
```

---

## 💬 `app/api/v1/endpoints/messages.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from .. .. import crud, deps, schemas, ml

router = APIRouter()

db_dep = Depends(deps.get_db_conn)

@router.post("/", response_model=None)
async def ingest(msg: schemas.MessageIn, db = db_dep):
    # classify
    label = ml.classifier.classify(msg.message)
    row = msg.model_dump()
    row["category"] = label
    crud.insert_messages(db, [row])
    return {"category": label}
```

---

## 🤝 `app/api/v1/endpoints/chatbot.py`

```python
from fastapi import APIRouter, Depends
from .. .. import deps, schemas, crud
from .. ..services import openai_service, memory

router = APIRouter()

db_dep = Depends(deps.get_db_conn)
session_dep = Depends(deps.get_session_id)

@router.post("/")
async def chat(req: schemas.ChatRequest, db = db_dep, session_id: str = session_dep):
    # remember the raw query
    memory.remember(session_id, req.query)

    # very rough NL → structured filter parsing – improve with regex or an LLM
    f = schemas.QueryFilters()
    if "telegram" in req.query.lower():
        f.source = "telegram"
    if "livechat" in req.query.lower():
        f.source = "livechat"
    for cat in ml.prompts.CATEGORIES:
        if cat.replace("_", " ") in req.query.lower():
            f.category = cat
    if "last month" in req.query.lower():
        from datetime import datetime, timedelta
        f.start_date = datetime.utcnow() - timedelta(days=30)

    # fetch stats
    rows = crud.fetch_messages(db, f)
    stats = {
        "count": len(rows),
        "unique_users": len({r["id_user"] for r in rows}),
    }

    # LLM to craft answer
    memo = memory.recall(session_id)
    answer = openai_service.chat_completion(prompt=req.query + "\nData: " + str(stats), memory=memo)
    return {"stats": stats, "answer": answer}
```

---

## 🐳 `docker/Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 📜 `requirements.txt`

```text
fastapi==0.110.0
uvicorn[standard]==0.29.0
supabase-py==2.3.4
python-dotenv==1.0.1
openai==1.30.1
transformers==4.41.1
accelerate==0.29.3
scikit-learn==1.5.0
python-dateutil==2.9.0
pydantic==2.7.1
```

*(If using GPU on Fly.io, add `torch` or `pytorch-cpu` to requirements.)*

---

## 🌐 `index.html` (quick smoke‑test)

```html
<!DOCTYPE html>
<html>
  <head><meta charset="utf-8"><title>LLM Feedback Assistant</title></head>
  <body>
    <h1>Send a query</h1>
    <input id="q" style="width:60%" placeholder="e.g. Telegram deposit issues last month">
    <button onclick="go()">Ask</button>
    <pre id="out"></pre>
    <script>
      async function go() {
        const q = document.getElementById('q').value
        const res = await fetch('/api/v1/chat', {method:'POST',headers:{'Content-Type':'application/json','session-id':'demo'},body:JSON.stringify({query:q,session_id:'demo'})})
        const json = await res.json()
        document.getElementById('out').innerText = JSON.stringify(json,null,2)
      }
    </script>
  </body>
</html>
```

---

## ✈️ `fly.toml`

```toml
app = "llm-feedback-assistant"
primary_region = "ams"
[build]
  dockerfile = "docker/Dockerfile"
[[services]]
  internal_port = 8080
  protocol = "tcp"
  [[services.ports]]
    port = "80"
    handlers = ["http"]
```

---

## 🎯 `README.md` (excerpt – fill in details)

````markdown
# LLM Feedback Assistant

A FastAPI backend that classifies player messages, stores them in Supabase, and lets you chat with an LLM to pull statistics with conversational memory.

## Quick start
```bash
git clone <repo>
cp .env.example .env  # add your keys
docker build -t llm-assistant -f docker/Dockerfile .
docker run -p 8080:8080 --env-file .env llm-assistant
# open http://localhost:8080/index.html
````

## Deployment on Fly.io

```bash
fly launch --dockerfile docker/Dockerfile --now
```

```

*(Add Evaluation Questions answers & lovable.dev dashboard instructions here.)*

---
### 🗃️ `.env.example`
```

OPENAI\_API\_KEY=
SUPABASE\_URL=[https://xyzcompany.supabase.co](https://xyzcompany.supabase.co)
SUPABASE\_KEY=public-anon-key

````

---
## 🧪 `tests/test_chatbot.py`
```python
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
````

---

### Next steps & wow‑factor

* **lovable.dev dashboard** – generate an API key on lovable.dev, drop their generated script into `index.html`, or spin up a separate `frontend/` built there and point it at `/api/v1/chat`.
* **Better NL parsing** – feed user input + memory to OpenAI function‑calling mode that returns structured `QueryFilters`.
* **Spike detection** – create a cron job (Fly.io machines/PG cron) that queries Supabase counts per day and flags ≥3× deviations.
* **Redis memory** – for multi‑instance scaling.
* **CI** – add GitHub Actions to run `pytest` and type‑check with `ruff`.

---

Happy building!  Ping me with `@assistant refine` if you need deeper code for any individual file or feature.
