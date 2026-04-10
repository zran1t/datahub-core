from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from serving_engine.app.dependencies import get_duckdb_client, get_settings
from serving_engine.query.duckdb_client import DuckDBClient
from serving_engine.schemas.candles import CandlesQueryResponse
from serving_engine.schemas.common import ErrorResponse
from serving_engine.services.candles_service import export_candles, get_candles
from serving_engine.settings.config import ServingSettings


router = APIRouter(prefix="/v1/data", tags=["candles"])

_JSON_ERROR_RESPONSES = {
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}

_EXPORT_ERROR_RESPONSES = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


@router.get("/candles", response_model=CandlesQueryResponse, responses=_JSON_ERROR_RESPONSES)
def get_candles_rows(
    symbol: str,
    start: str,
    end: str,
    settings: Annotated[ServingSettings, Depends(get_settings)],
    client: Annotated[DuckDBClient, Depends(get_duckdb_client)],
    exchange: str | None = None,
    interval: str | None = None,
    limit: int | None = None,
) -> CandlesQueryResponse:
    """
    執行單 symbol candles rows query。
    """
    result = get_candles(
        settings=settings,
        client=client,
        symbol=symbol,
        start=start,
        end=end,
        exchange=exchange,
        interval=interval,
        limit=limit,
    )
    return CandlesQueryResponse(**result)


@router.get("/candles/export", responses=_EXPORT_ERROR_RESPONSES)
def export_candles_file(
    symbols: str,
    start: str,
    end: str,
    settings: Annotated[ServingSettings, Depends(get_settings)],
    client: Annotated[DuckDBClient, Depends(get_duckdb_client)],
    exchange: str | None = None,
    interval: str | None = None,
) -> FileResponse:
    """
    執行 candles parquet export 並回傳檔案下載。
    """
    symbols_list = symbols.split(",")
    path = export_candles(
        settings=settings,
        client=client,
        symbols=symbols_list,
        start=start,
        end=end,
        exchange=exchange,
        interval=interval,
    )
    return FileResponse(
        path=str(path),
        media_type="application/octet-stream",
        filename=path.name,
    )
