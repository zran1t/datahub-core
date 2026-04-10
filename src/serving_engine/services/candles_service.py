from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from serving_engine.query.candles_query import export_candles_to_parquet, query_candles_rows
from serving_engine.query.duckdb_client import DuckDBClient
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


def _parse_iso8601_utc_to_ms(value: str) -> int:
    """
    將 timezone-aware ISO8601 時間字串轉成 UTC epoch ms。
    """
    dt_utc = _parse_iso8601_to_utc_datetime(value)
    return int(dt_utc.timestamp() * 1000)


def _parse_iso8601_to_utc_datetime(value: str) -> datetime:
    """
    將 timezone-aware ISO8601 時間字串轉成 UTC datetime。
    """
    text = str(value).strip()
    if not text:
        raise ValueError("時間字串不可為空")

    normalized = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"時間格式非法，必須為 ISO8601 UTC：{value}") from exc

    if dt.tzinfo is None:
        raise ValueError(f"時間字串必須包含時區資訊：{value}")

    return dt.astimezone(timezone.utc)


def _format_utc_datetime(dt: datetime) -> str:
    """
    將 UTC datetime 正規化成以 `Z` 結尾的 ISO8601 字串。
    """
    if dt.tzinfo is None:
        raise ValueError("datetime 必須包含時區資訊")
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.isoformat(timespec="seconds").replace("+00:00", "Z")


def _validate_time_range(start_ms: int, end_ms: int) -> None:
    """
    驗證時間範圍需滿足 start < end。
    """
    if start_ms >= end_ms:
        raise ValueError(f"start 必須早於 end：start_ms={start_ms}, end_ms={end_ms}")


def _validate_limit(limit: int | None, max_rows: int) -> int | None:
    """
    驗證 rows query limit。
    """
    if limit is None:
        return max_rows

    limit_value = int(limit)
    if limit_value <= 0:
        raise ValueError(f"limit 必須大於 0：{limit}")
    if limit_value > max_rows:
        raise ValueError(f"limit 不可超過 {max_rows}：{limit}")
    return limit_value


def _normalize_symbol(symbol: str) -> str:
    """
    正規化單一 symbol 輸入。
    """
    text = str(symbol).strip()
    if not text:
        raise ValueError("symbol 不可為空")
    return text


def _normalize_symbols(symbols: Sequence[str]) -> list[str]:
    """
    正規化 symbol 列表：移除空白、去重、保留原始順序。
    """
    out: list[str] = []
    seen: set[str] = set()

    for symbol in symbols:
        text = str(symbol).strip()
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append(text)

    if not out:
        raise ValueError("symbols 不可為空")
    return out


def _build_export_path(
    settings: ServingSettings,
) -> Path:
    """
    建立 server-controlled export output path。

    第一版採用簡單穩定命名策略，不把過多查詢資訊塞進檔名。
    """
    export_id = uuid4().hex[:12]
    return settings.export_root / "candles" / f"{export_id}.parquet"


def get_candles(
    settings: ServingSettings,
    client: DuckDBClient,
    *,
    symbol: str,
    start: str,
    end: str,
    exchange: str | None = None,
    interval: str | None = None,
    limit: int | None = None,
) -> dict:
    """
    執行單 symbol candles rows query，回傳 service-level result dict。
    """
    resolved_exchange = _resolve_exchange(settings, exchange)
    resolved_interval = _resolve_interval(settings, interval)
    _validate_supported_exchange(resolved_exchange)
    _validate_supported_interval(resolved_interval)

    normalized_symbol = _normalize_symbol(symbol)
    start_dt_utc = _parse_iso8601_to_utc_datetime(start)
    end_dt_utc = _parse_iso8601_to_utc_datetime(end)
    start_ms = int(start_dt_utc.timestamp() * 1000)
    end_ms = int(end_dt_utc.timestamp() * 1000)
    _validate_time_range(start_ms, end_ms)
    validated_limit = _validate_limit(limit, settings.json_query_max_rows)

    df = query_candles_rows(
        client=client,
        root=settings.canonical_candle_root,
        exchange=resolved_exchange,
        symbol=normalized_symbol,
        interval=resolved_interval,
        start_ms=start_ms,
        end_ms=end_ms,
        limit=validated_limit,
    )
    data = df.to_dict(orient="records")

    return {
        "dataset": "candles",
        "schema_version": "v1",
        "exchange": resolved_exchange,
        "symbol": normalized_symbol,
        "interval": resolved_interval,
        "start": _format_utc_datetime(start_dt_utc),
        "end": _format_utc_datetime(end_dt_utc),
        "rows": len(data),
        "data": data,
    }


def export_candles(
    settings: ServingSettings,
    client: DuckDBClient,
    *,
    symbols: Sequence[str],
    start: str,
    end: str,
    exchange: str | None = None,
    interval: str | None = None,
) -> Path:
    """
    執行多 symbol candles parquet export，回傳輸出檔案路徑。
    """
    resolved_exchange = _resolve_exchange(settings, exchange)
    resolved_interval = _resolve_interval(settings, interval)
    _validate_supported_exchange(resolved_exchange)
    _validate_supported_interval(resolved_interval)

    normalized_symbols = _normalize_symbols(symbols)
    start_ms = _parse_iso8601_utc_to_ms(start)
    end_ms = _parse_iso8601_utc_to_ms(end)
    _validate_time_range(start_ms, end_ms)

    export_path = _build_export_path(settings=settings)
    return export_candles_to_parquet(
        client=client,
        root=settings.canonical_candle_root,
        export_path=export_path,
        exchange=resolved_exchange,
        symbols=normalized_symbols,
        interval=resolved_interval,
        start_ms=start_ms,
        end_ms=end_ms,
    )
