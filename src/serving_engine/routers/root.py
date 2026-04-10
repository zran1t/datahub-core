from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(prefix="/v1", tags=["root"])


@router.get("")
def get_v1_index() -> dict:
    """
    回傳 v1 API 根索引。
    """
    return {
        "version": "v1",
        "sections": {
            "info": "/v1/info",
            "data": "/v1/data",
        },
    }


@router.get("/info")
def get_info_index() -> dict:
    """
    回傳 info 區塊索引。
    """
    return {
        "section": "info",
        "endpoints": [
            "/v1/info/version",
            "/v1/info/datasets",
            "/v1/info/schemas/{dataset}/{schema_version}",
            "/v1/info/availability/candles",
        ],
    }


@router.get("/data")
def get_data_index() -> dict:
    """
    回傳 data 區塊索引。
    """
    return {
        "section": "data",
        "endpoints": [
            "/v1/data/candles",
            "/v1/data/candles/export",
        ],
    }
