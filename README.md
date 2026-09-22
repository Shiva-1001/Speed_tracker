# Spend Tracker API

A small full-stack spend tracker built with **Python + FastAPI + SQLite** and a lightweight vanilla HTML/JavaScript UI.

## Features

- `POST /expenses` — create an expense
- `GET /expenses` — list expenses with optional category/date filters
- `GET /summary` — total spend, spend by category, and month-over-month change
- SQLite persistence
- Pydantic validation and consistent HTTP errors
- API-key authentication for API endpoints
- Automated tests covering validation, filtering, persistence, summary calculations, and authentication
- Minimal browser UI for adding expenses and viewing the summary

## Project structure

```text
spend-tracker/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── services.py
├── frontend/
│   └── index.html
├── tests/
│   ├── conftest.py
│   └── test_expenses.py
├── .claude/
│   ├── commands/
│   │   └── test.md
│   ├── rules/
│   │   └── python.md
│   └── ignore
├── .gitignore
├── CLAUDE.md
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- pip

## Run locally

### 1. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure authentication

The default development API key is:

```text
dev-secret-key
```

For a different key:

Linux/macOS:

```bash
export SPEND_TRACKER_API_KEY="your-secret-key"
```

Windows PowerShell:

```powershell
$env:SPEND_TRACKER_API_KEY="your-secret-key"
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

Open the UI at:

```text
http://127.0.0.1:8000/
```

Swagger/OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

The UI is preconfigured to use `dev-secret-key`. If you change the key, enter the new key in the UI.

## API examples

### Create an expense

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{
    "amount": 42.50,
    "category": "Food",
    "note": "Lunch",
    "date": "2026-09-22"
  }'
```

### List expenses

```bash
curl "http://127.0.0.1:8000/expenses?category=Food&from_date=2026-09-01&to_date=2026-09-30" \
  -H "X-API-Key: dev-secret-key"
```

### Get summary

```bash
curl "http://127.0.0.1:8000/summary?month=2026-09" \
  -H "X-API-Key: dev-secret-key"
```

The summary's month-over-month comparison is between the requested month and the immediately preceding calendar month. If `month` is omitted, the current server month is used.

## Validation rules

- Amount must be greater than zero and have at most two decimal places.
- Category is required and must be 1–50 characters.
- Note is optional and limited to 500 characters.
- Date must be a valid ISO calendar date (`YYYY-MM-DD`).
- Date range filters reject `from_date > to_date`.
- Invalid or missing API keys return `401 Unauthorized`.

## Design decisions

- **FastAPI** provides a small, typed REST API with automatic OpenAPI documentation.
- **SQLite** satisfies the persistence requirement without requiring an external database server.
- **Raw `sqlite3`** is used instead of an ORM to keep the assignment intentionally small and make the SQL/data model explicit.
- Money is stored as **integer cents** to avoid floating-point rounding problems.
- The service layer contains database/business logic separately from HTTP route handling, making the core calculations easier to test.
- A simple API key is included as the bonus authentication mechanism.
- The frontend is plain HTML/CSS/JavaScript so there is no build step.

## What I would do differently with more time

- Add user accounts so each user has isolated expenses instead of one shared ledger.
- Use PostgreSQL for production deployments.
- Add database migrations (for example Alembic).
- Add pagination and sorting to `GET /expenses`.
- Add update/delete expense endpoints.
- Add structured logging, rate limiting, and production secrets management.
- Add richer frontend validation and charts.
- Add Docker/CI configuration and coverage thresholds.

## AI assistance

AI tools were used to inspect the existing implementation, identify the response-serialization issue, and draft focused documentation. Their suggestions were reviewed against the requirements; unnecessary refactors and unrelated changes were rejected.
