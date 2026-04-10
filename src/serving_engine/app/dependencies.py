from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from serving_engine.query.duckdb_client import DuckDBClient
from serving_engine.settings.config import ServingSettings, load_settings


@lru_cache(maxsize=1)
def get_settings() -> ServingSettings:
    """
    載入並快取 serving runtime settings。
    """
    return load_settings()


def get_duckdb_client(
    settings: Annotated[ServingSettings, Depends(get_settings)],
) -> Iterator[DuckDBClient]:
    """
    提供 request-scoped DuckDB client。
    """
    client = DuckDBClient(
        database=settings.duckdb_database,
        read_only=settings.duckdb_read_only,
        config=settings.duckdb_config,
    )
    try:
        yield client
    finally:
        client.close()
