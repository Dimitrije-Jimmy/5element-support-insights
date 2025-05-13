# LLM Feedback Assistant

A FastAPI backend that classifies player messages, stores them in Supabase, and lets you chat with an LLM to pull statistics with conversational memory.

## Quick start
```bash
git clone <repo>
cp .env.example .env  # add your keys
docker build -t llm-assistant -f docker/Dockerfile .
docker run -p 8080:8080 --env-file .env llm-assistant
# open http://localhost:8080/index.html