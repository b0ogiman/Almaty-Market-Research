# Demo Scenario (Defense)

## Goal of Demo

Show how the system transforms raw local business data into actionable business recommendations for Almaty.

## Pre-Demo Checklist

- Run backend and dependencies (`docker-compose up` or local run).
- Open Swagger: `http://localhost:8000/docs`.
- Ensure API key is available for protected endpoints.
- Optional: keep DB viewer/logs open to show persisted records.

## Step-by-Step Defense Script

1. **Show system health**
   - Call: `GET /api/v1/health`
   - Highlight:
     - backend is running,
     - DB and Redis status are visible.

2. **Ingest market data (write-protected)**
   - Call: `POST /api/v1/data/ingest` with API key header.
   - Use small sample payload (2-5 rows).
   - Highlight:
     - authentication on write endpoint,
     - successful ingestion response with IDs.

3. **Run market analysis**
   - Call: `POST /api/v1/analysis/market`
   - Optional body: district/sector filter.
   - Highlight:
     - generated score,
     - insights object (demand/gap/trend/clusters).

4. **Generate opportunities (write-protected)**
   - Call: `POST /api/v1/opportunities/score` with API key.
   - Highlight:
     - scored opportunities with ranking fields,
     - score breakdown and metadata.

5. **Generate recommendations (write-protected)**
   - Call: `GET /api/v1/recommendations?limit=5` with API key.
   - Highlight:
     - recommendations built from opportunity results,
     - deterministic fallback exists even without OpenAI key.

6. **Show historical/paginated retrieval**
   - Call:
     - `GET /api/v1/data`
     - `GET /api/v1/analysis`
     - `GET /api/v1/opportunities`
   - Highlight:
     - persisted outputs,
     - reproducibility and traceability.

## Key Results to Emphasize

- Full pipeline works end-to-end:
  `collect/enrich -> analyze -> score -> recommend`.
- Reliability controls:
  - safe error handling at API layer,
  - transaction rollback,
  - cache invalidation on state changes.
- Security baseline:
  - API key on write operations.
