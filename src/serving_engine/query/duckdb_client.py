from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import duckdb


DuckDBParams = Sequence[Any] | Mapping[str, Any] | None


class DuckDBClient:
    """
    薄封裝 DuckDB 連線，提供 serving engine 共用的基本查詢介面。

    責任邊界：
    - 管理單一 DuckDB connection
    - 提供 execute / DataFrame 介面
    - 套用基本連線設定

    不負責：
    - dataset 路徑解析
    - candles SQL 組裝
    - COPY TO / export use case
    """

    def __init__(
        self,
        database: str | Path = ":memory:",
        *,
        read_only: bool = False,
        config: Mapping[str, Any] | None = None,
    ) -> None:
        self._database = str(database)
        self._read_only = read_only
        self._config = dict(config or {})
        self._connection: duckdb.DuckDBPyConnection | None = None

    @property
    def is_connected(self) -> bool:
        """
        回傳目前是否已建立連線。
        """
        return self._connection is not None

    def connect(self) -> duckdb.DuckDBPyConnection:
        """
        建立或回傳既有 DuckDB 連線。
        """
        if self._connection is None:
            connect_kwargs: dict[str, Any] = {
                "database": self._database,
                "config": self._config,
            }
            if self._database != ":memory:":
                connect_kwargs["read_only"] = self._read_only
            self._connection = duckdb.connect(**connect_kwargs)
        return self._connection

    def close(self) -> None:
        """
        關閉 DuckDB 連線。
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute(
        self,
        sql: str,
        params: DuckDBParams = None,
    ) -> duckdb.DuckDBPyConnection:
        """
        執行 SQL，回傳 DuckDB cursor-like connection 物件。
        """
        connection = self.connect()
        if params is None:
            return connection.execute(sql)
        return connection.execute(sql, params)

    def fetch_df(
        self,
        sql: str,
        params: DuckDBParams = None,
    ):
        """
        執行查詢並回傳 pandas DataFrame。

        適合小量查詢。
        """
        cursor = self.execute(sql, params=params)
        return cursor.fetch_df()

    def __enter__(self) -> DuckDBClient:
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
