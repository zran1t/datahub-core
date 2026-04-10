from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from serving_engine.schemas.common import DatasetCapability, SchemaField


class VersionInfoResponse(BaseModel):
    """
    `/v1/info/version` response shape。
    """

    service: str
    api_version: str
    supported_datasets: list[str]
    default_schema_versions: dict[str, str]


class SupportedDatasetsResponse(BaseModel):
    """
    `/v1/info/datasets` response shape。
    """

    datasets: list[DatasetCapability]


class SchemaInfoResponse(BaseModel):
    """
    `/v1/info/schemas/{dataset}/{schema_version}` response shape。
    """

    dataset: str
    schema_version: str
    description: str
    fields: list[SchemaField]
    time_semantics: dict[str, Any]
    symbol_rules: dict[str, Any]
    interval_constraints: dict[str, Any]


class CandlesAvailabilityResponse(BaseModel):
    """
    `/v1/info/availability/candles` response shape。
    """

    dataset: str
    schema_version: str
    exchange: str
    symbol: str
    interval: str
    available_start_ms: int
    available_end_ms: int
