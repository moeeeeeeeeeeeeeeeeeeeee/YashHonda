from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.db import reset_engine_cache
from app.main import create_app
from app.settings import get_settings


@pytest.fixture
def client(tmp_path, monkeypatch) -> Iterator[TestClient]:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()
    reset_engine_cache()

    with TestClient(create_app()) as test_client:
        yield test_client

    reset_engine_cache()
    get_settings.cache_clear()


def test_create_inquiry_then_quote(client: TestClient) -> None:
    inquiry_response = client.post(
        "/api/v1/inquiries",
        json={
            "customer": {"name": "Ashish", "mobile": "9822012345"},
            "source": "walk_in",
            "area": "Kothrud",
            "vehicle_type": "mc",
            "model_code": "ACTIVA_110_STD",
            "color": "Blue",
            "purchase_mode": "cash",
            "sales_executive": "Vinayak",
            "buying_when": "In Diwali",
        },
    )
    assert inquiry_response.status_code == 200
    inquiry_id = inquiry_response.json()["id"]

    quote_response = client.post(
        "/api/v1/quotes",
        json={
            "inquiry_id": inquiry_id,
            "model_code": "ACTIVA_110_STD",
            "color": "Blue",
            "purchase_mode": "cash",
            "include_extended_warranty": True,
            "include_optional_accessories": True,
            "include_helmet": True,
        },
    )

    assert quote_response.status_code == 200
    body = quote_response.json()
    assert body["quote_number"].startswith("YH-")
    assert body["preview"]["totals"]["grand_total"] == 103053.0
    assert body["pdf"]["bucket"] == "yash-honda-quote-docs-dev"

    pdf_response = client.get(f"/api/v1/quotes/{body['id']}/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.json()["storage_key"].endswith(".pdf")


def test_open_inquiries_endpoint(client: TestClient) -> None:
    client.post(
        "/api/v1/inquiries",
        json={
            "customer": {"name": "Lead One", "mobile": "9000000000"},
            "source": "google",
            "area": "Camp",
            "vehicle_type": "mc",
            "model_code": "UNICORN",
            "color": "Black",
            "purchase_mode": "cash",
            "sales_executive": "Sheel Gupta",
            "buying_when": "Immediate",
        },
    )

    response = client.get("/api/v1/inquiries/open")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
