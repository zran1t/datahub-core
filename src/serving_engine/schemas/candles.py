from __future__ import annotations

from pydantic import BaseModel


class CandleRow(BaseModel):
    """
    單筆 candles rows query row。
    """

    ts: int
    open: float
    high: float
    low: float
    close: float
    vol: float
    volCcy: float
    volCcyQuote: float


class CandlesQueryResponse(BaseModel):
    """
    `/v1/data/candles` JSON response shape。
    """

    dataset: str
    schema_version: str
    exchange: str
    symbol: str
    interval: str
    start: str
    end: str
    rows: int
    data: list[CandleRow]
