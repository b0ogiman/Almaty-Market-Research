## Deployment Guide – Almaty Market Research Platform

### 1. Prerequisites

- Docker and Docker Compose installed.
- For production, a domain name and TLS termination (e.g. via a reverse proxy or cloud load balancer).

### 2. Local Development with Docker Compose

From the repository root:

```bash
docker-compose up -d --build
```

Services:

- **api**: FastAPI backend (`http://localhost:8000`)
- **postgres**: PostgreSQL 15
- **redis**: Redis 7
- **frontend**: React SPA served by nginx (`http://localhost:3000`)

The frontend nginx config proxies `/api/*` to the backend service `api:8000`.

### 3. Environment Configuration

Backend configuration uses environment variables (see `app.config.Settings`):

- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_HOST`, `REDIS_PORT`
- `OPENAI_API_KEY` (optional, enables LLM features)
- `GOOGLE_MAPS_API_KEY` (optional, enables live Google Maps collection)

In Docker Compose these are already wired for local use; for production, set them explicitly in your orchestrator or `.env` files.

### 4. Production Image Builds

#### Backend

The root `Dockerfile` is a multi-stage Python build:

```bash
docker build -t almaty-market-api .
```

#### Frontend

The `frontend/Dockerfile` builds the React app and serves it via nginx with an `/api` reverse proxy:

```bash
cd frontend
docker build -t almaty-market-frontend .
```

### 5. Deploying to a Server

On a Linux host with Docker installed:

```bash
git clone <repo-url>
cd Almaty-Market-Research
docker-compose up -d --build
```

Optionally place a reverse proxy (e.g. Traefik, nginx, or a cloud load balancer) in front of:

- `frontend` service on port `3000` (public UI)
- `api` service on port `8000` (if exposing API directly)

### 6. CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

- Backend: installs Python deps and executes `pytest`.
- Frontend: installs Node deps, runs lint and `npm run build`.

You can extend this by adding image builds and pushes to a registry, then deploying from your preferred platform (e.g. ECS, Kubernetes, Azure Web Apps).

