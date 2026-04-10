# Serving Engine Overview

## 1. 定位

`serving_engine` 是 `datahub-core` 內負責「讀取 canonical dataset 並對外提供資料服務」的子系統。

它不負責：

- 抓取 raw 市場資料
- raw -> canonical normalization
- 研究 / 回測執行
- 任意 SQL 服務

它負責：

- 將 canonical dataset 封裝成穩定的讀取能力
- 支援小量 rows query
- 支援大量 parquet export
- 提供 dataset self-description 與 availability metadata

## 2. 核心原則

### Canonical-only

對外資料來源僅限 canonical dataset。raw dataset 不屬於 serving surface。

### Read-only

`serving_engine` 僅提供唯讀能力，不提供寫入、更新、刪除。

### Parquet-first

canonical dataset 的主要儲存與 bulk 交付格式都是 parquet。JSON 只作小量查詢回應。

### Dataset-first

外部介面以 dataset 能力為中心，不提供任意查詢語言。

## 3. 技術棧

- Parquet：canonical dataset physical storage
- DuckDB：embedded query engine
- FastAPI：HTTP API layer
- Uvicorn：ASGI runtime

其中：

- Parquet 是資料層
- DuckDB 是查詢層
- FastAPI 是服務層

## 4. 高層分層

```text
Client
  ↓
Routers / App Layer
  ↓
Services
  ↓
Query Layer
  ↓
Canonical Dataset (Parquet)
```

輔助模組：

- `settings/`：runtime config
- `catalog/`：dataset registry / schema registry
- `errors/`：API error mapping

## 5. 目前狀態

目前 v1 已落地完整的最小垂直切片：

- settings path / runtime config
- DuckDB client
- candles rows query
- candles parquet export
- candles availability query
- dataset/schema catalog
- services orchestration
- response schemas
- error handlers
- FastAPI routers / app factory
- CLI runner
- 基本 HTTP surface tests

目前仍屬後續工作：

- 更完整的 endpoint 文檔與 examples
- auth / rate limit / middleware
- 更多 datasets 與 intervals
- 更完整的 automated tests 與 bug sweep
