# Spend Tracker — Claude Project Guide

## Project goal

Maintain a small, production-minded Spend Tracker service with:

- Python REST API
- SQLite persistence
- Expense creation/listing
- Summary calculations
- Minimal browser UI
- Automated tests
- API-key authentication

Keep the implementation small and easy to review.

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- SQLite via Python's standard `sqlite3`
- Uvicorn
- pytest + FastAPI TestClient
- Vanilla HTML/CSS/JavaScript

## Repository layout

- `app/main.py`: FastAPI application, routes, auth, static-file serving
- `app/database.py`: SQLite connection/schema helpers
- `app/models.py`: request/response models and validation
- `app/services.py`: persistence and summary business logic
- `frontend/index.html`: minimal UI
- `tests/`: automated tests
- `.claude/rules/`: focused project rules
- `.claude/commands/`: reusable Claude commands

## Development commands

Create environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run API:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -q
```

## Coding standards

- Prefer small functions with one responsibility.
- Keep HTTP concerns in `main.py`; keep business/data logic in `services.py`.
- Use Pydantic models for request validation.
- Store money as integer cents, never as floating-point database values.
- Use parameterized SQL queries.
- Do not silently swallow database errors.
- Return useful HTTP status codes and concise error messages.
- Keep public API behavior documented in README and tests.
- Add or update tests when changing core behavior.

## Testing expectations

At minimum, test:

- valid expense creation
- invalid amount/date/category
- persistence
- category/date filtering
- summary category totals
- month-over-month calculation
- invalid date range
- missing/incorrect API key

## Security

- Never hardcode production credentials.
- Development may use `dev-secret-key` as the documented default.
- Read production API keys from `SPEND_TRACKER_API_KEY`.
- Never log API keys.
- Use parameterized SQL.

## Important behavior

`GET /summary?month=YYYY-MM` compares the selected calendar month with the immediately preceding calendar month.

If `month` is omitted, use the server's current calendar month.

Do not change this behavior without updating tests and README.
