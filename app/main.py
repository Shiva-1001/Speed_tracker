from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import ValidationError

from .database import DEFAULT_DB_PATH, get_connection, init_db
from .models import ExpenseCreate, ExpenseResponse, SummaryResponse
from .services import add_expense, list_expenses, summary_for_month

APP_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = APP_DIR.parent / "frontend"

app = FastAPI(
    title="Spend Tracker API",
    version="1.0.0",
    description="A small expense tracking REST API.",
)

API_KEY = os.getenv("SPEND_TRACKER_API_KEY", "dev-secret-key")


@app.on_event("startup")
def startup() -> None:
    init_db(DEFAULT_DB_PATH)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid API key",
        )


def validate_date_range(
    from_date: date | None, to_date: date | None
) -> None:
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="from_date must be on or before to_date",
        )


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
def create_expense(expense: ExpenseCreate) -> dict:
    with get_connection(DEFAULT_DB_PATH) as connection:
        return add_expense(connection, expense)


@app.get(
    "/expenses",
    response_model=list[ExpenseResponse],
    dependencies=[Depends(require_api_key)],
)
def get_expenses(
    category: str | None = Query(default=None, min_length=1, max_length=50),
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    validate_date_range(from_date, to_date)

    with get_connection(DEFAULT_DB_PATH) as connection:
        return list_expenses(connection, category, from_date, to_date)


@app.get(
    "/summary",
    response_model=SummaryResponse,
    dependencies=[Depends(require_api_key)],
)
def get_summary(
    month: str | None = Query(
        default=None,
        description="Calendar month in YYYY-MM format. Defaults to the server's current month.",
    ),
) -> dict:
    if month is None:
        selected = date.today()
    else:
        try:
            selected = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="month must use YYYY-MM format",
            )

    with get_connection(DEFAULT_DB_PATH) as connection:
        return summary_for_month(connection, selected.year, selected.month)
