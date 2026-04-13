from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.db import reset_engine_cache
from app.main import create_app
from app.seed_reference import run_seed
from app.settings import get_settings


@pytest.fixture
def seeded_client(tmp_path, monkeypatch) -> Iterator[TestClient]:
    db_path = tmp_path / "seeded.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()
    reset_engine_cache()
    run_seed()

    with TestClient(create_app()) as test_client:
        yield test_client

    reset_engine_cache()
    get_settings.cache_clear()


def test_quote_accepts_interchangeable_accessories(seeded_client: TestClient) -> None:
    inquiry_response = seeded_client.post(
        "/api/v1/inquiries",
        json={
            "customer": {"name": "Accessory Test", "mobile": "9000000001"},
            "source": "walk_in",
            "area": "Camp",
            "vehicle_type": "mc",
            "model_code": "ACTIVA_110_STD",
            "color": "Blue",
            "purchase_mode": "cash",
            "sales_executive": "Vinayak",
            "buying_when": "Next week",
        },
    )
    assert inquiry_response.status_code == 200
    inquiry_id = inquiry_response.json()["id"]

    quote_response = seeded_client.post(
        "/api/v1/quotes",
        json={
            "inquiry_id": inquiry_id,
            "model_code": "ACTIVA_110_STD",
            "color": "Blue",
            "purchase_mode": "cash",
            "selected_accessory_codes": [
                "MOD_VISOR::ACTIVA_110_STD",
                "STYLE_GRAPHICS_A::ACTIVA_110_STD",
            ],
        },
    )

    assert quote_response.status_code == 200
    lines = quote_response.json()["preview"]["lines"]
    accessory_lines = [line for line in lines if line["code"] == "accessory"]
    assert len(accessory_lines) == 2
