from __future__ import annotations


def auth_headers():
    return {"X-API-Key": "test-key"}


def test_create_and_persist_expense(client):
    payload = {
        "amount": "25.50",
        "category": "Food",
        "note": "Lunch",
        "date": "2026-09-22",
    }

    response = client.post("/expenses", json=payload, headers=auth_headers())

    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == 25.5
    assert body["category"] == "Food"

    listed = client.get("/expenses", headers=auth_headers())
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["note"] == "Lunch"


def test_invalid_amount_is_rejected(client):
    response = client.post(
        "/expenses",
        json={
            "amount": "0",
            "category": "Food",
            "date": "2026-09-22",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 422


def test_more_than_two_decimal_places_is_rejected(client):
    response = client.post(
        "/expenses",
        json={
            "amount": "10.123",
            "category": "Food",
            "date": "2026-09-22",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 422


def test_category_and_date_filters(client):
    headers = auth_headers()

    for payload in [
        {"amount": 10, "category": "Food", "date": "2026-09-01"},
        {"amount": 20, "category": "Travel", "date": "2026-09-10"},
        {"amount": 30, "category": "Food", "date": "2026-10-01"},
    ]:
        assert client.post("/expenses", json=payload, headers=headers).status_code == 201

    response = client.get(
        "/expenses?category=Food&from_date=2026-09-01&to_date=2026-09-30",
        headers=headers,
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["amount"] == 10


def test_invalid_date_range_is_rejected(client):
    response = client.get(
        "/expenses?from_date=2026-09-30&to_date=2026-09-01",
        headers=auth_headers(),
    )

    assert response.status_code == 400
    assert "from_date" in response.json()["detail"]


def test_summary_and_month_over_month_change(client):
    headers = auth_headers()

    expenses = [
        {"amount": 100, "category": "Food", "date": "2026-08-05"},
        {"amount": 50, "category": "Travel", "date": "2026-08-15"},
        {"amount": 120, "category": "Food", "date": "2026-09-02"},
        {"amount": 30, "category": "Travel", "date": "2026-09-03"},
    ]

    for expense in expenses:
        assert client.post("/expenses", json=expense, headers=headers).status_code == 201

    response = client.get("/summary?month=2026-09", headers=headers)

    assert response.status_code == 200
    body = response.json()

    assert body["total_spend"] == 150
    assert body["previous_month_total"] == 150
    assert body["month_over_month_change_percent"] == 0
    assert body["spend_by_category"] == [
        {"category": "Food", "total": 120},
        {"category": "Travel", "total": 30},
    ]


def test_summary_increase_is_calculated(client):
    headers = auth_headers()

    for expense in [
        {"amount": 100, "category": "Food", "date": "2026-08-01"},
        {"amount": 125, "category": "Food", "date": "2026-09-01"},
    ]:
        client.post("/expenses", json=expense, headers=headers)

    body = client.get("/summary?month=2026-09", headers=headers).json()

    assert body["month_over_month_change_percent"] == 25


def test_invalid_summary_month_is_rejected(client):
    response = client.get("/summary?month=2026-99", headers=auth_headers())

    assert response.status_code == 400
    assert response.json()["detail"] == "month must use YYYY-MM format"


def test_missing_or_invalid_api_key_is_rejected(client):
    assert client.get("/expenses").status_code == 401
    assert client.get(
        "/expenses", headers={"X-API-Key": "wrong-key"}
    ).status_code == 401
