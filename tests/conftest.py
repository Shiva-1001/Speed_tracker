from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).parent / "test_spend_tracker.db"


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("SPEND_TRACKER_API_KEY", "test-key")

    import app.main as main
    from app.database import init_db

    if TEST_DB.exists():
        TEST_DB.unlink()

    main.API_KEY = "test-key"
    main.DEFAULT_DB_PATH = TEST_DB

    init_db(TEST_DB)

    with TestClient(main.app) as test_client:
        yield test_client

    if TEST_DB.exists():
        TEST_DB.unlink()
