# AI-Powered Local Market Research Platform - Architecture

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER (FastAPI)                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐  │
│  │ Data Router │ │Analysis Router│ │Opportunity  │ │Recommendation│ │ Health    │  │
│  │ /api/v1/data│ │/api/v1/analysis│ │Router       │ │ Router       │ │ Router    │  │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬──────┘  │
└─────────┼───────────────┼───────────────┼───────────────┼──────────────┼─────────┘
          │               │               │               │              │
          ▼               ▼               ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER (Services)                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐  │
│  │ DataIngestion   │ │ MarketAnalysis  │ │ Opportunity     │ │ Recommendation │  │
│  │ Service         │ │ Service         │ │ ScoringService  │ │ Service        │  │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └───────┬────────┘  │
└───────────┼───────────────────┼───────────────────┼──────────────────┼───────────┘
            │                   │                   │                  │
            ▼                   ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AI LAYER (AI Services - MVP)                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                     │
│  │ MarketAnalysis  │ │ Opportunity     │ │ Recommendation  │                     │
│  │ Engine (stub)   │ │ Scorer (stub)   │ │ Engine (stub)   │                     │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘                     │
└───────────┼───────────────────┼───────────────────┼──────────────────────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                           │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │ PostgreSQL (SQLAlchemy ORM)      │  │ Redis (Caching - Ready)              │   │
│  │ - market_data                    │  │ - Analysis cache                     │   │
│  │ - analysis_results               │  │ - Opportunity cache                  │   │
│  │ - opportunities                  │  │ - Session/rate limiting              │   │
│  │ - recommendations                │  │                                       │   │
│  └─────────────────────────────────┘  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Explanation

### 2.1 Data Ingestion Flow
```
External Data Source → POST /api/v1/data/ingest → DataIngestionService 
    → Validate & Transform → PostgreSQL (market_data) → Optional Redis cache invalidation
```

### 2.2 Market Analysis Flow
```
POST /api/v1/analysis/market → Check Redis cache → Cache miss 
    → MarketAnalysisService → AI Layer (analysis engine) 
    → Store in PostgreSQL (analysis_results) → Cache result in Redis → Response
```

### 2.3 Opportunity Scoring Flow
```
POST /api/v1/opportunities/score → OpportunityScoringService 
    → Fetch market data → AI Layer (scoring engine) 
    → Store in PostgreSQL (opportunities) → Optional Redis cache → Response
```

### 2.4 Recommendation Flow
```
GET /api/v1/recommendations → Check Redis cache → RecommendationService 
    → AI Layer (recommendation engine) → Aggregate from opportunities 
    → Return top N recommendations
```

### 2.5 Health Check Flow
```
GET /health → HealthService → Check PostgreSQL connectivity 
    → Check Redis connectivity → Return status
```

## 3. Folder Structure

```
almaty-market-research/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   ├── logging_config.py       # Structured logging
│   ├── exceptions.py           # Custom exceptions & handlers
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── market_data.py
│   │   ├── analysis_result.py
│   │   ├── opportunity.py
│   │   └── recommendation.py
│   │
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── data.py
│   │   ├── analysis.py
│   │   ├── opportunity.py
│   │   └── common.py
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── data.py
│   │   ├── analysis.py
│   │   ├── opportunities.py
│   │   ├── recommendations.py
│   │   └── health.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── data_ingestion.py
│   │   ├── market_analysis.py
│   │   ├── opportunity_scoring.py
│   │   └── recommendation.py
│   │
│   └── ai/                     # AI layer (MVP stubs)
│       ├── __init__.py
│       ├── market_analysis_engine.py
│       ├── opportunity_scorer.py
│       └── recommendation_engine.py
│
├── alembic/                    # Database migrations (optional)
├── tests/
│   └── __init__.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── ARCHITECTURE.md
```

## 4. Database Schema

See `app/models/` for full SQLAlchemy definitions. Summary:

| Table | Purpose |
|-------|---------|
| market_data | Raw ingested market data (sector, district, metrics, source) |
| analysis_results | Cached market analysis outputs |
| opportunities | Scored business opportunities |
| recommendations | Aggregated recommendations with scores |

All tables include: id (UUID), created_at, updated_at. Soft-delete via is_active where appropriate.

### 8 Core REST API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/data/ingest | Data ingestion (bulk) |
| GET | /api/v1/data | List ingested data (paginated) |
| POST | /api/v1/analysis/market | Run market analysis |
| GET | /api/v1/analysis | List analysis results |
| POST | /api/v1/opportunities/score | Score opportunities |
| GET | /api/v1/opportunities | List opportunities |
| GET | /api/v1/recommendations | Get top recommendations |
| GET | /api/v1/health | Health check (DB + Redis) |
