# Customer Management System

REST API + web UI for managing customers, orders, and categories.

- **Backend:** FastAPI, SQLAlchemy 2, PostgreSQL, JWT auth (`python-jose`)
- **Frontend:** React 19 + TypeScript, built with Vite (served by FastAPI — no CORS needed)
- **Infra:** Docker Compose (Postgres + API)

## Features

- Customer CRUD with pagination (`GET /api/customers?page=&page_size=`)
- Orders per customer, status filter, and status updates
- Category listing
- JWT-protected write endpoints; browsing is public
- Swagger UI at `/docs`, health check at `/health`

## Quick start (Docker)

```bash
# 1. build the frontend bundle (the container serves frontend/dist)
cd frontend && npm install && npm run build && cd ..

# 2. start Postgres + API
docker compose up --build
```

Open http://localhost:8000 — the UI is served at `/`, the API docs at `/docs`.

## Local development

### 1. Database

```bash
docker compose up -d db
```

Connection settings come from `.env` (see below); the default database is `customer_management`.

### 2. Backend

```bash
python -m venv venv
venv\Scripts\pip install -r backend\requirements.txt   # macOS/Linux: pip install -r backend/requirements.txt

cd backend
uvicorn main:app --reload                               # run from backend/
```

The API listens on http://localhost:8000. Tables are created automatically on startup.
Run the backend from `backend/` (modules use flat imports, e.g. `from config import config`).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173, proxies /api + /health to :8000
```

Other scripts: `npm run build` (type-check + bundle into `frontend/dist`), `npm run typecheck`.

To see the production bundle locally, run `npm run build` and restart the backend —
it serves `frontend/dist` at `/`.

## Configuration

Copy the values into `.env` / `backend/.env` (never commit these — `.env` is gitignored).

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | Full SQLAlchemy URL (overrides the `POSTGRES_*` set) | built from the values below |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | DB credentials | `postgres` / — / `customer_management` |
| `POSTGRES_HOST` / `POSTGRES_PORT` | DB host/port | `127.0.0.1` / `5432` |
| `SECRET_KEY` | JWT signing key | `change-me-to-a-long-random-secret` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `ENV` / `DEBUG` | Runtime flags | `development` / `True` |
| `FRONTEND_DIR` | Static frontend directory (set to `/frontend` in Docker) | `frontend/dist`, else `frontend/` |

## API

All bodies are JSON. Endpoints marked 🔒 require `Authorization: Bearer <token>`.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/auth/login` | `{email, password}` → `{access_token, token_type}` |
| GET | `/api/customers` | Paginated list → `{data, total_count, page, size}` |
| POST | `/api/customers` 🔒 | Create `{name, email, phone?}` (alias: `POST /api/customers/create`) |
| GET | `/api/customers/{id}` | Customer detail |
| POST | `/api/customers/{id}` 🔒 | Partial update `{name?, email?, phone?}` |
| GET | `/api/customers/{id}/orders` | `{orders, count}` for that customer |
| GET | `/api/orders` | `?status=&page=&page_size=` → `{orders, total_count, page, page_size}` |
| GET | `/api/orders/{id}` | Order detail |
| POST | `/api/orders/{id}` 🔒 | Update status, body `{status: "pending" \| "completed" \| "cancelled"}` |
| GET | `/api/categories` | `{categories, count}` |
| GET | `/api/categories/{id}` | Category detail |
| GET | `/health` | DB-backed health check (also at `/api/health`) |

```bash
# example
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"secret"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s -X POST localhost:8000/api/customers \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Jane Doe","email":"jane@example.com","phone":"555-0100"}'
```

> Windows note: PowerShell mangles JSON passed to `curl.exe`. Use `Invoke-RestMethod`
> instead:
> `Invoke-RestMethod -Uri http://localhost:8000/api/auth/login -Method Post -ContentType 'application/json' -Body '{"email":"you@example.com","password":"secret"}'`

## Tests

```bash
venv\Scripts\python -m pytest tests -q     # macOS/Linux: python -m pytest tests -q
```

Covers the health check, model registration, JWT round-trip, and DB session factory.
An instance of Postgres must be reachable for the health check.

## Project structure

```
├── backend/
│   ├── app.py              # FastAPI app, /health, static frontend mount
│   ├── routes.py           # All /api endpoints
│   ├── schemas.py          # Pydantic request bodies
│   ├── config.py           # Env-based configuration
│   ├── models/             # SQLAlchemy models (Customer, Order, Category)
│   └── services/           # db (engine/session) + auth (JWT)
├── frontend/               # React + TS app (Vite)
│   ├── src/
│   │   ├── App.tsx         # Tabs, session, toasts
│   │   ├── api.ts          # Typed fetch client + auth handling
│   │   └── components/     # Login, Customers, Orders, Categories
│   └── dist/               # Build output served by FastAPI (gitignored)
├── tests/                  # pytest suite
└── docker-compose.yml      # db + api
```

## Notes & limitations

- `AuthService.authenticate_user` is a placeholder: it validates the email format and
  that a password was supplied, but there is no user table yet — any credentials mint a
  token. Wire it to a `users` table (and switch to bcrypt/argon2) before production.
- Orders and categories are read-only over the API; no create/delete endpoints yet.
- Passwords are hashed with salted SHA-256 (placeholder — swap for bcrypt/argon2).
