# City Museum catalog (FastAPI demo)

Small REST API for tracking which works hang in which rooms. Everything lives in memory: restarting the process clears the catalog. The point of the repo is to show FastAPI structure (routers, dependencies, Pydantic models), automatic OpenAPI docs, bearer auth on **all** API paths, Docker, and a basic test suite.

## Requirements

- Python 3.10+
- Docker (optional, for container run)

## Configuration

| Variable | Meaning |
|----------|---------|
| `API_TOKEN` | Secret string used as the **Bearer** token for every API route (`/health`, `/exhibits`, …). |

If unset, the app defaults to `dev-token-change-in-prod` (fine for local play; set a real value in Docker/production).

You can put values in a `.env` file in the project root (`pydantic-settings` loads it automatically).

## Setup

```bash
cd DataAPI
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the server (local)

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000  
- Swagger UI: http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc  

In Swagger, open **Authorize** first, choose **HTTPBearer**, and paste **only the token value** (no `Bearer ` prefix). Use the same value as `API_TOKEN`. Without that, **Try it out** on any endpoint returns **403** (missing header) or **401** (wrong token).

The HTML for `/docs` and the OpenAPI JSON at `/openapi.json` are still served without auth so the UI can load; only the **API** paths require a token. To hide the schema in production, put the app behind a reverse proxy or turn off docs (`docs_url=None` in `FastAPI()`).

On startup the app loads two sample records so `/docs` has something to try against after you authorize. Automated tests use their own empty store via dependency overrides, so they do not rely on that seed data.

## Run with Docker

```bash
cd DataAPI
docker compose up --build
```

By default `docker-compose.yml` sets `API_TOKEN` to `change-me-in-production`. Override when running:

```bash
API_TOKEN=my-secret docker compose up --build
```

The API listens on port **8000** on the host.

## Tests

```bash
pytest
```

Tests force `API_TOKEN=test-secret` in `conftest.py` and send `Authorization: Bearer test-secret` on every request.

## Response shape

Success responses use a single envelope:

```json
{
  "success": true,
  "message": "…",
  "data": { },
  "meta": { "page": 1, "limit": 50, "total": 12 }
}
```

`meta` appears on **GET `/exhibits`** (pagination: `page`, `limit`, `total`). Other successful calls omit `meta` when not needed. `data` may be `null` (for example after a delete).

Errors use:

```json
{
  "success": false,
  "message": "…",
  "error": { "code": "SOME_CODE", "details": [ { "field": "…", "message": "…" } ] }
}
```

`details` is present for validation failures (`VALIDATION_ERROR`, HTTP 422). Typical codes include `AUTH_INVALID_CREDENTIALS` (401), `AUTH_REQUIRED` (403), `EXHIBIT_NOT_FOUND` (404), `INTERNAL_ERROR` (500).

## Endpoints (overview)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | Bearer | Liveness check |
| GET | `/exhibits` | Bearer | List exhibits (filters + `page` / `limit`; `meta` has totals) |
| GET | `/exhibits/rooms/summary` | Bearer | Count exhibits per room |
| GET | `/exhibits/{id}` | Bearer | Fetch one exhibit |
| POST | `/exhibits` | Bearer | Add an exhibit |
| PATCH | `/exhibits/{id}` | Bearer | Partial update |
| DELETE | `/exhibits/{id}` | Bearer | Remove |

## Layout

- `app/core/config.py` — settings (`API_TOKEN`)  
- `app/core/responses.py` — JSON helpers for the success/error envelope  
- `app/api/auth.py` — Bearer dependency (applied to every API router)  
- `app/models/` — Pydantic request/response models  
- `app/services/catalog.py` — in-memory storage and filtering  
- `app/api/routes/` — route handlers  
- `app/main.py` — FastAPI app, router wiring, global exception handlers  
- `tests/` — pytest + `TestClient`  
- `Dockerfile`, `docker-compose.yml` — container run  

If you turn this into a real service, replace `CatalogStore` with a database layer and keep the Pydantic models as your public contract; swap the static bearer token for proper user accounts or OAuth if you need that.
