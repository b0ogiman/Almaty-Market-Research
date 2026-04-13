# System Architecture

## 1. Main Processing Flow

Core business flow implemented in the project:

`collect -> enrich -> analyze -> score -> recommend`

### 1.1 Flow Explanation

1. **Collect**
   - Source adapters (mock Avito and optional Google Maps) fetch business listings.
   - Validation and deduplication run before persistence.
   - Main modules: `app/collectors/*`, `app/jobs/scheduler.py`.

2. **Enrich**
   - Listings are enriched with:
     - mapped district (`district_mapped`)
     - normalized category (`category_normalized`)
     - sentiment score (`sentiment_score`)
   - Main modules: `app/enrichment/*`, integrated in `app/collectors/pipeline.py`.

3. **Analyze**
   - Analysis uses enriched listings from DB.
   - Metrics include demand, competition-driven gap score, clustering, and trend detection.
   - Main modules: `app/services/market_analysis.py`, `app/ai/market_analysis_engine.py`, `app/analytics/*`.

4. **Score Opportunities**
   - Opportunities are generated from analytics signals by district/category segment.
   - Persisted in PostgreSQL and cached with TTL in Redis.
   - Main modules: `app/services/opportunity_scoring.py`.

5. **Recommend**
   - Recommendations are generated from top opportunities.
   - Uses LLM when configured; falls back to deterministic heuristic engine.
   - Main modules: `app/services/recommendation.py`, `app/llm/*`, `app/ai/recommendation_engine.py`.

## 2. Layered Architecture

- **API Layer (`app/routers`)**
  - Input validation, auth dependency for write endpoints, safe HTTP responses.
- **Service Layer (`app/services`)**
  - Core orchestration, persistence boundaries, cache usage/invalidation.
- **Analytics Layer (`app/analytics`)**
  - Reusable metric calculators and clustering/trend logic.
- **Data Pipeline Layer (`app/collectors`, `app/enrichment`, `app/jobs`)**
  - Collection jobs and preparation of structured listing data.
- **AI/LLM Layer (`app/ai`, `app/llm`)**
  - Domain logic for analysis/recommendation generation with graceful fallback.
- **Data Layer (`app/models`, `app/database`, `app/core/redis_client.py`)**
  - PostgreSQL for persistence, Redis for cache.

## 3. Module Map (Brief)

- `app/main.py`: app bootstrap, CORS, exception handlers, router registration, scheduler lifecycle.
- `app/config.py`: environment-driven settings (security, DB, Redis, cache, scheduler, LLM).
- `app/security.py`: API key protection for mutating endpoints.
- `app/database.py`: async SQLAlchemy session/transaction management.
- `app/routers/*`: endpoint handlers (`/data`, `/analysis`, `/opportunities`, `/recommendations`, `/health`).
- `app/services/*`: business use-cases (ingestion, analysis, scoring, recommendation).
- `app/collectors/*`: source adapters, cleaning, dedup, persistence pipeline.
- `app/enrichment/*`: district mapper, category normalizer, sentiment scorer.
- `app/analytics/*`: demand score, competition index, market gap, clustering, trends.
- `app/llm/*`: OpenAI client, prompts, recommendation/summary services.
- `app/jobs/scheduler.py`: scheduled collection job and cache invalidation.
- `tests/*`: unit and API/integration tests for reliability.

## 4. Reliability and Safety Design

- **Transactions**
  - Write flows use DB session commit/rollback boundaries.
  - Batch writes are atomic in ingestion and collection pipeline.
- **Cache consistency**
  - State-changing operations invalidate:
    - `analysis:`
    - `opportunities:`
    - `recommendations:`
- **Fault tolerance**
  - Routers convert unexpected exceptions into safe `500` responses.
  - LLM layer has fallback path to deterministic recommendation engine.
- **Security baseline**
  - API key required for write endpoints.
  - Production startup checks enforce critical environment configuration.

## 5. API Surface (Core)

- `POST /api/v1/data/ingest`
- `GET /api/v1/data`
- `POST /api/v1/analysis/market`
- `GET /api/v1/analysis`
- `POST /api/v1/opportunities/score`
- `GET /api/v1/opportunities`
- `GET /api/v1/recommendations`
- `GET /api/v1/health`
