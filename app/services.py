from __future__ import annotations

import sqlite3
from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .models import ExpenseCreate

CENT = Decimal("0.01")


def money_to_cents(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cents_to_money(cents: int) -> Decimal:
    return (Decimal(cents) / Decimal(100)).quantize(CENT)


def add_expense(connection: sqlite3.Connection, expense: ExpenseCreate) -> dict:
    amount_cents = money_to_cents(expense.amount)

    cursor = connection.execute(
        """
        INSERT INTO expenses (amount_cents, category, note, expense_date)
        VALUES (?, ?, ?, ?)
        """,
        (amount_cents, expense.category, expense.note, expense.date.isoformat()),
    )
    connection.commit()

    row = connection.execute(
        """
        SELECT id, amount_cents, category, note, expense_date
        FROM expenses
        WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()

    return {
        "id": row["id"],
        "amount": cents_to_money(row["amount_cents"]),
        "category": row["category"],
        "note": row["note"],
        "date": date.fromisoformat(row["expense_date"]),
    }


def list_expenses(
    connection: sqlite3.Connection,
    category: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    query = """
        SELECT id, amount_cents, category, note, expense_date
        FROM expenses
        WHERE 1 = 1
    """
    params: list[object] = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if from_date:
        query += " AND expense_date >= ?"
        params.append(from_date.isoformat())

    if to_date:
        query += " AND expense_date <= ?"
        params.append(to_date.isoformat())

    query += " ORDER BY expense_date DESC, id DESC"

    rows = connection.execute(query, params).fetchall()

    return [
        {
            "id": row["id"],
            "amount": cents_to_money(row["amount_cents"]),
            "category": row["category"],
            "note": row["note"],
            "date": date.fromisoformat(row["expense_date"]),
        }
        for row in rows
    ]


def month_bounds(year: int, month: int) -> tuple[date, date]:
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def total_for_range(
    connection: sqlite3.Connection, start: date, end: date
) -> int:
    row = connection.execute(
        """
        SELECT COALESCE(SUM(amount_cents), 0) AS total
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    return int(row["total"])


def summary_for_month(
    connection: sqlite3.Connection, year: int, month: int
) -> dict:
    start, end = month_bounds(year, month)
    previous_year, previous_month_number = previous_month(year, month)
    previous_start, previous_end = month_bounds(
        previous_year, previous_month_number
    )

    current_total = total_for_range(connection, start, end)
    previous_total = total_for_range(connection, previous_start, previous_end)

    rows = connection.execute(
        """
        SELECT category, SUM(amount_cents) AS total
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
        GROUP BY category
        ORDER BY total DESC, category ASC
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()

    if previous_total == 0:
        change = None if current_total == 0 else None
    else:
        change = (
            (Decimal(current_total - previous_total) / Decimal(previous_total))
            * Decimal(100)
        ).quantize(CENT)

    return {
        "month": f"{year:04d}-{month:02d}",
        "total_spend": cents_to_money(current_total),
        "spend_by_category": [
            {
                "category": row["category"],
                "total": cents_to_money(int(row["total"])),
            }
            for row in rows
        ],
        "previous_month_total": cents_to_money(previous_total),
        "month_over_month_change_percent": change,
    }
