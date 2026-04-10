from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from serving_engine.app.dependencies import get_settings
from serving_engine.schemas.common import ErrorResponse
from serving_engine.schemas.info import (
    CandlesAvailabilityResponse,
    SchemaInfoResponse,
    SupportedDatasetsResponse,
    VersionInfoResponse,
)
from serving_engine.services.info_service import (
    get_candles_availability_info,
    get_schema_info,
    get_supported_datasets,
    get_version_info,
)
from serving_engine.settings.config import ServingSettings


router = APIRouter(prefix="/v1/info", tags=["info"])

_ERROR_RESPONSES = {
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


@router.get("/version", response_model=VersionInfoResponse, responses=_ERROR_RESPONSES)
def get_version() -> VersionInfoResponse:
    """
    回傳 serving engine v1 版本資訊。
    """
    result = get_version_info()
    return VersionInfoResponse(**result)


@router.get("/datasets", response_model=SupportedDatasetsResponse, responses=_ERROR_RESPONSES)
def get_datasets() -> SupportedDatasetsResponse:
    """
    回傳目前支援的 datasets。
    """
    result = get_supported_datasets()
    return SupportedDatasetsResponse(**result)


@router.get(
    "/schemas/{dataset}/{schema_version}",
    response_model=SchemaInfoResponse,
    responses=_ERROR_RESPONSES,
)
def get_schema(
    dataset: str,
    schema_version: str,
) -> SchemaInfoResponse:
    """
    回傳指定 dataset/schema_version 的 schema metadata。
    """
    result = get_schema_info(dataset=dataset, schema_version=schema_version)
    return SchemaInfoResponse(**result)


@router.get(
    "/availability/candles",
    response_model=CandlesAvailabilityResponse | None,
    responses=_ERROR_RESPONSES,
)
def get_candles_availability(
    symbol: str,
    settings: Annotated[ServingSettings, Depends(get_settings)],
    exchange: str | None = None,
    interval: str | None = None,
) -> CandlesAvailabilityResponse | None:
    """
    回傳 candles availability metadata。
    """
    result = get_candles_availability_info(
        settings=settings,
        symbol=symbol,
        exchange=exchange,
        interval=interval,
    )
    if result is None:
        return None
    return CandlesAvailabilityResponse(**result)
