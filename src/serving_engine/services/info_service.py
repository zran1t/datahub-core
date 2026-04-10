from __future__ import annotations

from serving_engine.catalog.datasets import (
    get_dataset_info,
    is_supported_dataset,
    list_supported_datasets,
)
from serving_engine.catalog.schema_registry import get_schema_info as lookup_schema_info
from serving_engine.catalog.schema_registry import has_schema
from serving_engine.query.availability_query import get_candles_availability
from serving_engine.settings.config import ServingSettings


def _resolve_exchange(settings: ServingSettings, exchange: str | None) -> str:
    """
    解析最終 exchange 值。
    """
    if exchange is None:
        return settings.default_exchange
    text = exchange.strip()
    return text or settings.default_exchange


def _resolve_interval(settings: ServingSettings, interval: str | None) -> str:
    """
    解析最終 interval 值。
    """
    if interval is None:
        return settings.default_interval
    text = interval.strip()
    return text or settings.default_interval


def _validate_supported_dataset(dataset: str) -> None:
    """
    驗證 dataset 是否受支援。
    """
    if not is_supported_dataset(dataset):
        raise ValueError(f"不支援的 dataset：{dataset}")


def _validate_supported_exchange(exchange: str) -> None:
    """
    v1 目前只接受 `okx`。
    """
    if exchange != "okx":
        raise ValueError(f"目前僅支援 exchange=okx：{exchange}")


def _validate_supported_interval(interval: str) -> None:
    """
    v1 目前只接受 `1m`。
    """
    if interval != "1m":
        raise ValueError(f"目前僅支援 interval=1m：{interval}")


def _normalize_symbol(symbol: str) -> str:
    """
    正規化單一 symbol。
    """
    text = str(symbol).strip()
    if not text:
        raise ValueError("symbol 不可為空")
    return text


def _validate_schema_request(dataset: str, schema_version: str) -> None:
    """
    驗證 dataset 與 schema version 是否存在於 registry。
    """
    _validate_supported_dataset(dataset)
    if not has_schema(dataset, schema_version):
        raise ValueError(f"找不到 schema：dataset={dataset}, schema_version={schema_version}")


def get_version_info() -> dict:
    """
    回傳 serving engine v1 的版本資訊。
    """
    datasets = list_supported_datasets()
    return {
        "service": "datahub-serving",
        "api_version": "v1",
        "supported_datasets": [dataset.name for dataset in datasets],
        "default_schema_versions": {
            dataset.name: dataset.default_schema_version
            for dataset in datasets
        },
    }


def get_supported_datasets() -> dict:
    """
    回傳目前支援的 datasets 與 capability metadata。
    """
    return {
        "datasets": [
            {
                "name": dataset.name,
                "default_schema_version": dataset.default_schema_version,
                "query_enabled": dataset.query_enabled,
                "export_enabled": dataset.export_enabled,
                "availability_enabled": dataset.availability_enabled,
            }
            for dataset in list_supported_datasets()
        ]
    }


def get_schema_info(
    *,
    dataset: str,
    schema_version: str,
) -> dict:
    """
    回傳指定 dataset/schema_version 的 schema metadata。
    """
    _validate_schema_request(dataset, schema_version)
    schema = lookup_schema_info(dataset, schema_version)
    if schema is None:
        raise ValueError(f"找不到 schema：dataset={dataset}, schema_version={schema_version}")

    return {
        "dataset": schema.dataset,
        "schema_version": schema.schema_version,
        "description": schema.description,
        "fields": [
            {
                "name": field.name,
                "type": field.type,
                "description": field.description,
                "nullable": field.nullable,
            }
            for field in schema.fields
        ],
        "time_semantics": dict(schema.time_semantics),
        "symbol_rules": dict(schema.symbol_rules),
        "interval_constraints": dict(schema.interval_constraints),
    }


def get_candles_availability_info(
    settings: ServingSettings,
    *,
    symbol: str,
    exchange: str | None = None,
    interval: str | None = None,
) -> dict | None:
    """
    回傳 candles availability metadata；無資料時回傳 `None`。
    """
    dataset = get_dataset_info("candles")
    if dataset is None:
        raise ValueError("找不到 dataset registry：candles")

    resolved_exchange = _resolve_exchange(settings, exchange)
    resolved_interval = _resolve_interval(settings, interval)
    _validate_supported_exchange(resolved_exchange)
    _validate_supported_interval(resolved_interval)
    normalized_symbol = _normalize_symbol(symbol)

    availability = get_candles_availability(
        root=settings.canonical_candle_root,
        exchange=resolved_exchange,
        symbol=normalized_symbol,
        interval=resolved_interval,
    )
    if availability is None:
        return None

    return {
        "dataset": dataset.name,
        "schema_version": dataset.default_schema_version,
        "exchange": availability.exchange,
        "symbol": availability.symbol,
        "interval": availability.interval,
        "available_start_ms": availability.available_start_ms,
        "available_end_ms": availability.available_end_ms,
    }
