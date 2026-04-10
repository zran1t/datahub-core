from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any


_DORMA_PREFIX = "@dorma/"


@dataclass(slots=True)
class ServingSettings:
    """
    Serving engine 的最小 runtime config。

    設計原則：
    - 支援 `@dorma/...` 作為本地開發別名
    - 支援以環境變數覆寫成絕對路徑，方便 Linux/Ubuntu 部署
    - 所有路徑在 settings 層統一 resolve 成 `Path`
    """

    canonical_candle_root: Path
    export_root: Path
    default_exchange: str
    default_interval: str
    json_query_max_rows: int
    duckdb_database: str
    duckdb_read_only: bool
    duckdb_config: dict[str, Any] = field(default_factory=dict)


def _get_env_str(name: str, default: str) -> str:
    """
    讀取字串環境變數，未提供時回傳預設值。
    """
    value = os.getenv(name)
    if value is None:
        return default
    text = value.strip()
    return text or default


def _get_env_int(name: str, default: int) -> int:
    """
    讀取整數環境變數，未提供時回傳預設值。
    """
    value = os.getenv(name)
    if value is None:
        return default
    text = value.strip()
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"環境變數 {name} 無法解析為整數：{value}") from exc


def _get_env_bool(name: str, default: bool) -> bool:
    """
    讀取布林環境變數，接受常見真假字串。
    """
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"環境變數 {name} 無法解析為布林值：{value}")


def _detect_dorma_root() -> Path | None:
    """
    嘗試找出 dorma 根目錄。

    使用順序：
    1. `DORMA_ROOT`
    2. 從目前工作目錄一路往上找含有 `cores/` 的路徑
    3. 從目前檔案位置一路往上找含有 `cores/` 的路徑

    這個 helper 只服務 `@dorma/...` 路徑解析，不應成為部署時的硬依賴。
    """
    env_root = os.getenv("DORMA_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for start in (Path.cwd().resolve(), Path(__file__).resolve().parent):
        for candidate in (start, *start.parents):
            if (candidate / "cores").is_dir():
                return candidate

    return None


def _resolve_platform_path(value: str | Path) -> Path:
    """
    將設定中的路徑值解析成實際 `Path`。

    支援：
    - `@dorma/...`：本地開發別名，會相對於 dorma root 解析
    - 絕對路徑：直接使用
    - 相對路徑：相對於目前 process working directory 解析
    """
    path_text = str(value).strip()
    if not path_text:
        raise ValueError("路徑設定不可為空")

    if path_text.startswith(_DORMA_PREFIX):
        dorma_root = _detect_dorma_root()
        if dorma_root is None:
            raise RuntimeError(
                "無法解析 @dorma 路徑：找不到 dorma root。"
                " 請設定 DORMA_ROOT 或改用絕對路徑。"
            )
        relative_path = path_text.removeprefix(_DORMA_PREFIX)
        return (dorma_root / relative_path).resolve()

    return Path(path_text).expanduser().resolve()


def load_settings() -> ServingSettings:
    """
    載入 serving engine 第一版所需的最小設定。
    """
    return ServingSettings(
        canonical_candle_root=_resolve_platform_path(
            _get_env_str(
                "DATAHUB_CANONICAL_CANDLE_ROOT",
                "@dorma/data/canonical/candle",
            )
        ),
        export_root=_resolve_platform_path(
            _get_env_str(
                "DATAHUB_EXPORT_ROOT",
                "@dorma/workspace/datahub_exports",
            )
        ),
        default_exchange=_get_env_str("DATAHUB_DEFAULT_EXCHANGE", "okx"),
        default_interval=_get_env_str("DATAHUB_DEFAULT_INTERVAL", "1m"),
        json_query_max_rows=_get_env_int("DATAHUB_JSON_QUERY_MAX_ROWS", 10_000),
        duckdb_database=_get_env_str("DATAHUB_DUCKDB_DATABASE", ":memory:"),
        duckdb_read_only=_get_env_bool("DATAHUB_DUCKDB_READ_ONLY", False),
    )
