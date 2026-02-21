# AI-Powered Local Market Research Platform – Almaty

MVP backend for local market research and business opportunity identification in Almaty.

## Quick Start

### Local (PostgreSQL + Redis required)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment (copy .env.example to .env)
cp .env.example .env

# Initialize database
python -m scripts.init_db

# Run API
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up -d
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/data/ingest` | Bulk ingest market data |
| GET | `/api/v1/data` | List ingested data |
| POST | `/api/v1/analysis/market` | Run market analysis |
| GET | `/api/v1/analysis` | List analysis results |
| POST | `/api/v1/opportunities/score` | Score opportunities |
| GET | `/api/v1/opportunities` | List opportunities |
| GET | `/api/v1/recommendations` | Get top recommendations |
| GET | `/api/v1/health` | Health check |

See `ARCHITECTURE.md` for full design.
