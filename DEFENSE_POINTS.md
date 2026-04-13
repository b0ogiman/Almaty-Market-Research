# Defense Explanation Points

## 1) Why this architecture?

- **Layered design** separates concerns:
  - routers handle HTTP,
  - services handle orchestration,
  - analytics/AI modules handle computation,
  - DB/cache modules handle persistence/performance.
- This makes the system easier to test, maintain, and extend for post-diploma production work.
- Modular structure allowed incremental implementation (MVP first, advanced analytics next) without rewriting core backend.

## 2) How caching works

- Redis is used for computed outputs where recomputation is expensive:
  - analysis results,
  - opportunity results,
  - recommendations.
- Cache entries use TTL to avoid indefinite staleness.
- On any state-changing write operation, related cache prefixes are invalidated:
  - `analysis:`
  - `opportunities:`
  - `recommendations:`
- This gives a practical balance: good response speed with controlled freshness.

## 3) How reliability is ensured

- **API robustness**
  - Router-level try/except prevents unhandled service crashes from breaking endpoints.
  - Unexpected failures are returned as safe `500 Internal server error`.
- **Transaction safety**
  - DB sessions commit/rollback around request scope.
  - Batch write flows are atomic to reduce partial-write risk.
- **Tests**
  - Unit tests cover analytics, enrichment, collectors, and evaluation.
  - API integration tests cover success, validation errors, auth failures, and failure scenarios.
  - End-to-end integration test validates pipeline flow (with environment-aware skip when DB config is absent).

## 4) How AI/LLM is used

- Analytics layer provides deterministic market signals:
  - demand score,
  - competition index,
  - market gap score,
  - clustering and trend indicators.
- Recommendation stage can use OpenAI (when key is configured) for richer narrative suggestions.
- If LLM is unavailable, system falls back to deterministic recommendation logic, so core functionality remains stable.

## 5) Practical message to examiners

- The project is not only a prototype model, but an operational decision-support pipeline.
- It demonstrates engineering completeness:
  - data pipeline,
  - analytics,
  - API productization,
  - reliability and security baseline,
  - test-backed behavior for live demo confidence.
