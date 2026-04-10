from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from serving_engine.query.duckdb_client import DuckDBClient


_CANDLE_COLUMNS = (
    "ts",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "volCcy",
    "volCcyQuote",
)

_EMPTY_CANDLES_DF_SQL = """
SELECT
    CAST(NULL AS BIGINT) AS ts,
    CAST(NULL AS DOUBLE) AS open,
    CAST(NULL AS DOUBLE) AS high,
    CAST(NULL AS DOUBLE) AS low,
    CAST(NULL AS DOUBLE) AS close,
    CAST(NULL AS DOUBLE) AS vol,
    CAST(NULL AS DOUBLE) AS volCcy,
    CAST(NULL AS DOUBLE) AS volCcyQuote
WHERE FALSE
""".strip()


def _floor_ms_to_utc_date(value_ms: int) -> date:
    """
    將 epoch milliseconds 對應到 UTC 日期。
    """
    dt = datetime.fromtimestamp(value_ms / 1000, tz=timezone.utc)
    return dt.date()


def _iter_utc_dates_in_range(start_ms: int, end_ms: int) -> list[str]:
    """
    依 start inclusive / end exclusive 規則列出需掃描的 UTC 日期。
    """
    if start_ms >= end_ms:
        raise ValueError(f"start_ms 必須早於 end_ms：start_ms={start_ms}, end_ms={end_ms}")

    current = _floor_ms_to_utc_date(start_ms)
    last = _floor_ms_to_utc_date(end_ms - 1)
    out: list[str] = []
    while current <= last:
        out.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return out


def _build_day_path(
    root: Path,
    exchange: str,
    symbol: str,
    interval: str,
    day: str,
) -> Path:
    """
    依 canonical candles physical layout 建立單日 parquet 路徑。
    """
    year = day[:4]
    month = day[5:7]
    return root / exchange / symbol / interval / year / month / f"{day}.parquet"


def _resolve_existing_day_paths(
    root: Path,
    exchange: str,
    symbol: str,
    interval: str,
    start_ms: int,
    end_ms: int,
) -> list[Path]:
    """
    解析指定時間區間內實際存在的 parquet day paths。

    serving query 不在這一層做 completeness fail-fast，只回目前可查到的檔案。
    """
    out: list[Path] = []
    for day in _iter_utc_dates_in_range(start_ms, end_ms):
        path = _build_day_path(root, exchange, symbol, interval, day)
        if path.exists():
            out.append(path)
    return out


def _quote_path(path: Path) -> str:
    """
    將 server 端自行 resolve 的 path 轉成 SQL 字串常值。
    """
    escaped = str(path).replace("'", "''")
    return f"'{escaped}'"


def _build_read_parquet_source_sql(paths: Sequence[Path]) -> str:
    """
    將 parquet path list 組成 DuckDB read_parquet(...) source。
    """
    if not paths:
        raise ValueError("read_parquet source 不可為空")

    quoted_paths = ", ".join(_quote_path(path) for path in paths)
    return f"read_parquet([{quoted_paths}])"


def _build_single_symbol_select_sql(
    paths: Sequence[Path],
    start_ms: int,
    end_ms: int,
    limit: int | None = None,
) -> tuple[str, list[object]]:
    """
    建立單 symbol rows query 的 DuckDB SELECT SQL。
    """
    if not paths:
        raise ValueError("單 symbol 查詢至少需要一個 parquet path")

    limit_clause = ""
    params: list[object] = [start_ms, end_ms]
    if limit is not None:
        limit_value = int(limit)
        if limit_value < 0:
            raise ValueError(f"limit 不可為負數：{limit}")
        limit_clause = "\nLIMIT ?"
        params.append(limit_value)

    source_sql = _build_read_parquet_source_sql(paths)
    columns_sql = ",\n    ".join(_CANDLE_COLUMNS)
    sql = (
        "SELECT\n"
        f"    {columns_sql}\n"
        f"FROM {source_sql}\n"
        "WHERE ts >= ? AND ts < ?\n"
        "ORDER BY ts ASC"
        f"{limit_clause}"
    )
    return sql, params


def _build_multi_symbol_select_sql(
    symbol_to_paths: Sequence[tuple[str, Sequence[Path]]],
    start_ms: int,
    end_ms: int,
) -> tuple[str, list[object]]:
    """
    建立多 symbol export 的 DuckDB SELECT SQL。
    """
    if not symbol_to_paths:
        raise ValueError("多 symbol export 至少需要一組來源")

    union_parts: list[str] = []
    params: list[object] = []

    for symbol, paths in symbol_to_paths:
        if not paths:
            continue

        source_sql = _build_read_parquet_source_sql(paths)
        union_parts.append(
            "SELECT\n"
            "    ? AS symbol,\n"
            "    ts,\n"
            "    open,\n"
            "    high,\n"
            "    low,\n"
            "    close,\n"
            "    vol,\n"
            "    volCcy,\n"
            "    volCcyQuote\n"
            f"FROM {source_sql}\n"
            "WHERE ts >= ? AND ts < ?"
        )
        params.extend([symbol, start_ms, end_ms])

    if not union_parts:
        raise ValueError("多 symbol export 沒有任何可用來源")

    union_sql = "\nUNION ALL\n".join(union_parts)
    sql = (
        "SELECT\n"
        "    symbol,\n"
        "    ts,\n"
        "    open,\n"
        "    high,\n"
        "    low,\n"
        "    close,\n"
        "    vol,\n"
        "    volCcy,\n"
        "    volCcyQuote\n"
        "FROM (\n"
        f"{union_sql}\n"
        ") AS unioned\n"
        "ORDER BY symbol ASC, ts ASC"
    )
    return sql, params


def _build_copy_sql(select_sql: str, export_path: Path) -> str:
    """
    建立 DuckDB COPY (...) TO ... SQL。
    """
    quoted_export_path = _quote_path(export_path)
    return (
        f"COPY ({select_sql}) TO {quoted_export_path} "
        "(FORMAT PARQUET, COMPRESSION ZSTD)"
    )


def _empty_candles_df(client: DuckDBClient):
    """
    回傳具固定 canonical 欄位的空 DataFrame。
    """
    return client.fetch_df(_EMPTY_CANDLES_DF_SQL)


def _dedupe_symbols(symbols: Sequence[str]) -> list[str]:
    """
    去重並保留 symbols 原始順序。
    """
    out: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        if symbol in seen:
            continue
        seen.add(symbol)
        out.append(symbol)
    return out


def query_candles_rows(
    client: DuckDBClient,
    root: Path,
    exchange: str,
    symbol: str,
    interval: str,
    start_ms: int,
    end_ms: int,
    limit: int | None = None,
):
    """
    查詢單 symbol candles rows，回傳 pandas DataFrame。
    """
    root = Path(root).expanduser().resolve()
    paths = _resolve_existing_day_paths(
        root=root,
        exchange=exchange,
        symbol=symbol,
        interval=interval,
        start_ms=start_ms,
        end_ms=end_ms,
    )
    if not paths:
        return _empty_candles_df(client)

    sql, params = _build_single_symbol_select_sql(
        paths=paths,
        start_ms=start_ms,
        end_ms=end_ms,
        limit=limit,
    )
    return client.fetch_df(sql, params=params)


def export_candles_to_parquet(
    client: DuckDBClient,
    root: Path,
    export_path: Path,
    exchange: str,
    symbols: Sequence[str],
    interval: str,
    start_ms: int,
    end_ms: int,
) -> Path:
    """
    將多 symbol candles 直接以 DuckDB COPY 匯出成單一 parquet 檔。
    """
    root = Path(root).expanduser().resolve()
    export_path = Path(export_path).expanduser().resolve()
    if not symbols:
        raise ValueError("symbols 不可為空")

    symbol_to_paths: list[tuple[str, Sequence[Path]]] = []
    for symbol in _dedupe_symbols(symbols):
        paths = _resolve_existing_day_paths(
            root=root,
            exchange=exchange,
            symbol=symbol,
            interval=interval,
            start_ms=start_ms,
            end_ms=end_ms,
        )
        if paths:
            symbol_to_paths.append((symbol, paths))

    if not symbol_to_paths:
        raise FileNotFoundError("找不到符合條件的 candles parquet 檔案，無法匯出")

    select_sql, params = _build_multi_symbol_select_sql(
        symbol_to_paths=symbol_to_paths,
        start_ms=start_ms,
        end_ms=end_ms,
    )
    copy_sql = _build_copy_sql(select_sql, export_path)

    export_path.parent.mkdir(parents=True, exist_ok=True)
    client.execute(copy_sql, params=params)
    return export_path
