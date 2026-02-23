# API Documentation – Almaty Market Research Platform

## Base URLs

- Backend API: `http://localhost:8000`
- When running via Docker Compose: same, fronted by Docker network.

OpenAPI / Swagger:

- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`
- OpenAPI JSON: `GET /openapi.json`

These are configured in `app.main:app` via FastAPI’s `docs_url`, `redoc_url`, and default `openapi_url`.

## Authentication

The MVP API is unauthenticated and intended for internal/controlled use.

## Health

- **GET** `/api/v1/health`
  - **200 OK**
  - Response body (example):
    ```json
    {
      "status": "healthy",
      "version": "0.1.0",
      "database": "ok",
      "redis": "ok",
      "detail": null
    }
    ```

## Data Ingestion

- **POST** `/api/v1/data/ingest`
  - Bulk-ingest raw market data records.
  - Request body (simplified):
    ```json
    {
      "items": [
        {
          "source": "google_maps",
          "sector": "food_service",
          "district": "Bostandyk",
          "payload": { "name": "Cafe", "rating": 4.6 }
        }
      ]
    }
    ```
  - **201 Created** on success.

- **GET** `/api/v1/data`
  - Query parameters:
    - `limit` (int, optional)
    - `offset` (int, optional)
    - `sector` (str, optional)
    - `district` (str, optional)
  - **200 OK** with paginated list of ingested data.

## Market Analysis

- **POST** `/api/v1/analysis/market`
  - Triggers market analysis pipeline (uses analytics + AI layer).
  - Request body (simplified):
    ```json
    {
      "sector": "food_service",
      "district": "Bostandyk"
    }
    ```
  - **201 Created** with created analysis result.

- **GET** `/api/v1/analysis`
  - Lists existing analysis results.
  - Supports pagination query params (`limit`, `offset`).

## Opportunity Scoring

- **POST** `/api/v1/opportunities/score`
  - Computes opportunity scores using demand, competition, and market gap.
  - Request body (simplified):
    ```json
    {
      "sector": "food_service",
      "district": "Bostandyk"
    }
    ```
  - **201 Created** with opportunities created for the segment.

- **GET** `/api/v1/opportunities`
  - Returns current opportunity objects, optionally paginated.

## Recommendations

- **GET** `/api/v1/recommendations`
  - Returns ranked recommendations.
  - When OpenAI is configured, uses LLM-backed recommendation service; otherwise, heuristic engine.
  - Response is a list of objects like:
    ```json
    {
      "id": "uuid",
      "title": "New cafe near metro",
      "district": "Bostandyk",
      "sector": "food_service",
      "score": 0.87
    }
    ```

## Error Handling

Errors are returned as structured JSON:

```json
{
  "error": "ValidationError",
  "message": "Invalid payload",
  "detail": {
    "...": "..."
  }
}
```

FastAPI’s validation errors are normalized via custom handlers in `app.exceptions`, and all unhandled exceptions are wrapped in a generic 500 error with a safe message for clients.

