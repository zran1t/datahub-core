from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from serving_engine.catalog.datasets import get_default_schema_version


@dataclass(frozen=True, slots=True)
class SchemaFieldInfo:
    """
    單一 schema 欄位的 metadata。
    """

    name: str
    type: str
    description: str
    nullable: bool = False


@dataclass(frozen=True, slots=True)
class DatasetSchemaInfo:
    """
    dataset schema metadata 摘要。
    """

    dataset: str
    schema_version: str
    description: str
    fields: tuple[SchemaFieldInfo, ...]
    time_semantics: dict[str, Any]
    symbol_rules: dict[str, Any]
    interval_constraints: dict[str, Any]


_SCHEMA_REGISTRY: dict[str, dict[str, DatasetSchemaInfo]] = {
    "candles": {
        "v1": DatasetSchemaInfo(
            dataset="candles",
            schema_version="v1",
            description="Historical OHLCV canonical dataset for research, backtest, and serving.",
            fields=(
                SchemaFieldInfo("ts", "int64", "UTC epoch milliseconds of candle open time."),
                SchemaFieldInfo("open", "float64", "Open price."),
                SchemaFieldInfo("high", "float64", "High price."),
                SchemaFieldInfo("low", "float64", "Low price."),
                SchemaFieldInfo("close", "float64", "Close price."),
                SchemaFieldInfo("vol", "float64", "Trade volume."),
                SchemaFieldInfo("volCcy", "float64", "Volume in base currency."),
                SchemaFieldInfo("volCcyQuote", "float64", "Volume in quote currency."),
            ),
            time_semantics={
                "timestamp_field": "ts",
                "timestamp_unit": "epoch_ms",
                "timezone": "UTC",
                "timestamp_meaning": "candle_open_time",
            },
            symbol_rules={
                "canonical_naming": True,
                "examples": ["BTC-USDT-SPOT", "BTC-USDT-SWAP"],
                "case_sensitive": True,
            },
            interval_constraints={
                "supported_intervals": ["1m"],
                "v1_only": True,
            },
        ),
    },
}


def get_schema_info(dataset: str, schema_version: str) -> DatasetSchemaInfo | None:
    """
    取得指定 dataset/schema_version 的 schema metadata。
    """
    versions = _SCHEMA_REGISTRY.get(dataset)
    if versions is None:
        return None
    return versions.get(schema_version)


def has_schema(dataset: str, schema_version: str) -> bool:
    """
    判斷指定 schema 是否存在。
    """
    return get_schema_info(dataset, schema_version) is not None


def list_schema_versions(dataset: str) -> list[str]:
    """
    列出指定 dataset 目前支援的 schema versions。
    """
    versions = _SCHEMA_REGISTRY.get(dataset)
    if versions is None:
        return []
    return list(versions.keys())


def get_default_schema_info(dataset: str) -> DatasetSchemaInfo | None:
    """
    透過 datasets registry 的 default schema version 取得 schema metadata。
    """
    default_version = get_default_schema_version(dataset)
    if default_version is None:
        return None
    return get_schema_info(dataset, default_version)
