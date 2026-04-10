# DuckDB Client

本文件描述 `query/duckdb_client.py` 在 serving engine 中的角色。

## 1. 定位

`DuckDBClient` 是一個很薄的 execution adapter。

它的責任是：

- 管理單一 DuckDB connection
- 提供基本 SQL 執行介面
- 提供小量查詢用的 DataFrame 取回能力

它不是：

- ORM
- generic repository layer
- dataset-aware query object
- export orchestration layer

## 2. 提供的能力

目前提供：

- `connect()`
- `close()`
- `execute(sql, params)`
- `fetch_df(sql, params)`

這組介面足以支撐：

- query layer 小量 rows query
- query layer `COPY TO` 執行

## 3. 為什麼刻意保持很薄

`DuckDBClient` 不懂：

- candles physical layout
- availability
- API payload
- export output policy

這些都應該留在 dataset-specific query module 或更上層的 service。

保持它薄的好處：

- 不把 dataset 邏輯塞進底層 client
- 不讓所有需求都回流到一個通用 DB layer
- 後續若調整 query 策略，影響面較小

## 4. 與其他模組的關係

- `settings/config.py` 提供 DuckDB runtime config
- `candles_query.py` 使用 `DuckDBClient` 做 rows query 與 `COPY TO`
- `availability_query.py` 不依賴 `DuckDBClient`

## 5. 非目標

目前 v1 不在 `DuckDBClient` 內提供：

- Arrow export
- dataset registry
- schema introspection
- path resolve
- API error handling
