from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from fastapi.testclient import TestClient

from serving_engine.app.dependencies import get_settings
from serving_engine.app.factory import create_app


def _write_day_file(root: Path, exchange: str, symbol: str, interval: str, day: str, rows: dict) -> None:
    year = day[:4]
    month = day[5:7]
    path = root / exchange / symbol / interval / year / month / f"{day}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table(rows), path)


@pytest.fixture()
def client_with_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    canonical_root = tmp_path / "canonical" / "candle"
    export_root = tmp_path / "exports"

    base_ts = 1743120000000
    _write_day_file(
        canonical_root,
        "okx",
        "BTC-USDT-SWAP",
        "1m",
        "2025-03-28",
        {
            "ts": [base_ts, base_ts + 60_000],
            "open": [100.0, 101.0],
            "high": [101.0, 102.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "vol": [1.5, 2.0],
            "volCcy": [0.15, 0.2],
            "volCcyQuote": [150.0, 204.0],
        },
    )
    _write_day_file(
        canonical_root,
        "okx",
        "ETH-USDT-SWAP",
        "1m",
        "2025-03-28",
        {
            "ts": [base_ts],
            "open": [200.0],
            "high": [201.0],
            "low": [199.0],
            "close": [200.5],
            "vol": [3.0],
            "volCcy": [0.3],
            "volCcyQuote": [601.5],
        },
    )

    monkeypatch.setenv("DATAHUB_CANONICAL_CANDLE_ROOT", str(canonical_root))
    monkeypatch.setenv("DATAHUB_EXPORT_ROOT", str(export_root))
    get_settings.cache_clear()

    client = TestClient(create_app(), raise_server_exceptions=False)
    try:
        yield client
    finally:
        get_settings.cache_clear()


def test_rows_query_returns_json_payload(client_with_data: TestClient) -> None:
    response = client_with_data.get(
        "/v1/data/candles",
        params={
            "symbol": "BTC-USDT-SWAP",
            "start": "2025-03-28T00:00:00Z",
            "end": "2025-03-28T00:02:00Z",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rows"] == 2
    assert payload["start"] == "2025-03-28T00:00:00Z"
    assert payload["end"] == "2025-03-28T00:02:00Z"
    assert payload["data"][0]["ts"] == 1743120000000
    assert "symbol" not in payload["data"][0]


def test_export_endpoint_returns_parquet_file(client_with_data: TestClient) -> None:
    response = client_with_data.get(
        "/v1/data/candles/export",
        params={
            "symbols": "BTC-USDT-SWAP,ETH-USDT-SWAP",
            "start": "2025-03-28T00:00:00Z",
            "end": "2025-03-28T00:02:00Z",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert response.content[:4] == b"PAR1"


def test_availability_endpoint_returns_metadata(client_with_data: TestClient) -> None:
    response = client_with_data.get(
        "/v1/info/availability/candles",
        params={"symbol": "BTC-USDT-SWAP"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["available_start_ms"] == 1743120000000
    assert payload["available_end_ms"] == 1743206400000


def test_request_validation_error_is_mapped(client_with_data: TestClient) -> None:
    response = client_with_data.get(
        "/v1/data/candles",
        params={
            "symbol": "BTC-USDT-SWAP",
            "start": "2025-03-28T00:00:00Z",
            "end": "2025-03-28T00:02:00Z",
            "limit": "oops",
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "INVALID_ARGUMENT"
    assert "query.limit" in payload["error"]["message"]


def test_openapi_uses_error_response_model_without_default_422(
    client_with_data: TestClient,
) -> None:
    response = client_with_data.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    get_candles_operation = payload["paths"]["/v1/data/candles"]["get"]
    responses = get_candles_operation["responses"]

    assert "422" not in responses
    assert responses["400"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ErrorResponse"
    )
    assert "HTTPValidationError" not in payload["components"]["schemas"]
