from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re


_DAY_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.parquet$")


@dataclass(slots=True)
class CandlesAvailability:
    """
    單一 exchange / symbol / interval 的 candles availability metadata。
    """

    exchange: str
    symbol: str
    interval: str
    available_start_ms: int
    available_end_ms: int


def _build_symbol_interval_dir(
    root: Path,
    exchange: str,
    symbol: str,
    interval: str,
) -> Path:
    """
    建立 canonical candles 的 symbol-interval 目錄路徑。
    """
    return root / exchange / symbol / interval


def _iter_day_files(symbol_interval_dir: Path) -> list[Path]:
    """
    掃描並回傳符合 canonical 命名規則的日 parquet 檔。

    只接受：
    - <year>/<month>/YYYY-MM-DD.parquet
    不符合規則的檔案一律忽略。
    """
    out: list[Path] = []
    for path in symbol_interval_dir.glob("*/*/*.parquet"):
        if not path.is_file():
            continue
        if _DAY_FILE_PATTERN.fullmatch(path.name) is None:
            continue
        out.append(path)
    return out


def _parse_day_from_file_path(path: Path) -> date:
    """
    從 canonical 日 parquet 檔名解析 UTC 日期。
    """
    return date.fromisoformat(path.stem)


def _day_start_ms(day: date) -> int:
    """
    將 UTC 日期轉成當天 00:00:00 UTC 的 epoch ms。
    """
    dt = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def _day_end_exclusive_ms(day: date) -> int:
    """
    將 UTC 日期轉成下一天 00:00:00 UTC 的 epoch ms。
    """
    return _day_start_ms(day + timedelta(days=1))


def get_candles_availability(
    root: Path,
    exchange: str,
    symbol: str,
    interval: str,
) -> CandlesAvailability | None:
    """
    依 canonical day partition file presence 計算 candles availability。

    找不到任何合法日檔時回傳 `None`。
    """
    root = Path(root).expanduser().resolve()
    symbol_interval_dir = _build_symbol_interval_dir(
        root=root,
        exchange=exchange,
        symbol=symbol,
        interval=interval,
    )
    if not symbol_interval_dir.exists():
        return None

    day_files = _iter_day_files(symbol_interval_dir)
    if not day_files:
        return None

    days = sorted(_parse_day_from_file_path(path) for path in day_files)
    earliest_day = days[0]
    latest_day = days[-1]

    return CandlesAvailability(
        exchange=exchange,
        symbol=symbol,
        interval=interval,
        available_start_ms=_day_start_ms(earliest_day),
        available_end_ms=_day_end_exclusive_ms(latest_day),
    )
