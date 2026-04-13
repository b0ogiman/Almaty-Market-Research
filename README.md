# AI-Powered Platform for Local Market Research in Almaty

AI-powered diploma project for identifying local business opportunities in Almaty using data collection, enrichment, analytics, scoring, and recommendation generation.

## Project Overview

The platform helps answer one core question:

`Where should a new business be launched in Almaty, and why?`

It does this by combining:
- market data ingestion and business listing collection,
- automated enrichment (district, category, sentiment),
- analytics (demand, competition, market gap, clustering, trends),
- opportunity scoring,
- recommendation generation (LLM-enabled with fallback).

## Architecture Modules

- **API layer (`app/routers`)**: FastAPI endpoints for data, analysis, opportunities, recommendations, and health.
- **Service layer (`app/services`)**: Orchestration and business rules, including caching and persistence boundaries.
- **Data collection (`app/collectors`)**: External listing ingestion with validation and deduplication.
- **Enrichment (`app/enrichment`)**: District mapping, category normalization, sentiment scoring.
- **Analytics (`app/analytics`)**: Demand, competition index, market gap scoring, clustering, trend detection.
- **LLM layer (`app/llm`)**: OpenAI wrapper + structured recommendation/summary prompting with safe fallback.
- **Persistence (`app/models`, `app/database`)**: PostgreSQL via SQLAlchemy.
- **Caching (`app/core/redis_client.py`)**: Redis-based TTL caching and invalidation.
- **Background jobs (`app/jobs`)**: APScheduler for periodic collection.

Detailed architecture and flow: `ARCHITECTURE.md`.

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (async), Pydantic
- **Database**: PostgreSQL
- **Cache**: Redis
- **Scheduling**: APScheduler
- **AI/LLM**: OpenAI API (optional, fallback available)
- **Testing**: pytest, FastAPI TestClient
- **Containerization**: Docker, docker-compose

## How to Run (Step-by-Step)

### 1) Local Run (Backend)

1. Create and activate virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` and set required values
   - `POSTGRES_HOST`
   - `POSTGRES_PORT`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `API_KEY` (for protected write endpoints)
4. Initialize database schema
   ```bash
   python -m scripts.init_db
   ```
5. Start API
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 2) Docker Run

```bash
docker-compose up --build
```

After startup:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## API Overview

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/api/v1/data/ingest` | Ingest market metrics | API key required |
| GET | `/api/v1/data` | List market metrics | Public |
| POST | `/api/v1/analysis/market` | Run market analysis | Public |
| GET | `/api/v1/analysis` | List analysis records | Public |
| POST | `/api/v1/opportunities/score` | Generate opportunity scores | API key required |
| GET | `/api/v1/opportunities` | List opportunities | Public |
| GET | `/api/v1/recommendations` | Generate/list recommendations | API key required |
| GET | `/api/v1/health` | Health status (DB/Redis) | Public |

Docs:
- `ARCHITECTURE.md`
- `API_DOCUMENTATION.md`
- `DEPLOYMENT_GUIDE.md`
- `DEMO_SCENARIO.md`
- `DEFENSE_POINTS.md`
