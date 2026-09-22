from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    note: str | None = Field(default=None, max_length=500)
    date: date

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value.as_tuple().exponent < -2:
            raise ValueError("amount must have at most two decimal places")
        return value

    @field_validator("category", "note")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("text fields cannot be blank")
        return stripped


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    category: str
    note: str | None
    date: date


class CategorySummary(BaseModel):
    category: str
    total: float


class SummaryResponse(BaseModel):
    month: str
    total_spend: float
    spend_by_category: list[CategorySummary]
    previous_month_total: float
    month_over_month_change_percent: float | None
