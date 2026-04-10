# Serving Engine API v1

本文件是 `serving_engine` v1 的對外 API 總覽。

詳細 endpoint payload、response format 與 error model 會在後續拆到獨立文件；本文件只描述 v1 的整體 contract 與範圍。

## 1. v1 目標

v1 目標是提供統一、穩定、可程式化存取的 historical market data entry point。

目前 v1 以 canonical dataset 為唯一資料來源，先聚焦：

- info endpoints
- candles rows query
- candles parquet export

## 2. 設計原則

- Canonical-only
- Read-only
- Dataset-first
- Parquet-first

這表示：

- API 不提供 raw dataset
- API 不提供寫入能力
- API 不提供任意 SQL
- JSON 只作小量資料查詢
- Parquet 作 bulk export

## 3. v1 範圍

目前 v1 僅支援：

- dataset：`candles`
- interval：`1m`

目前 v1 不包含：

- 即時資料
- CSV export
- 任意 SQL
- 認證與權限控制
- completeness / missing days 對外查詢

## 4. URL 結構總覽

```text
/v1
/v1/info
/v1/data

/v1/info/version
/v1/info/datasets
/v1/info/schemas/{dataset}/{schema_version}
/v1/info/availability/{dataset}

/v1/data/candles
/v1/data/candles/export
```

## 5. 核心時間契約

- request time format：ISO8601 UTC
- dataset time format：epoch milliseconds
- `start`：inclusive
- `end`：exclusive
- 預設排序：依時間升冪

`availability` 也遵守同樣的 end-exclusive 語意。

## 6. 資料交付模型

### `GET /v1/data/candles`

用途：

- 單 symbol 小量 rows query

交付格式：

- JSON

### `GET /v1/data/candles/export`

用途：

- 多 symbol bulk export

交付格式：

- parquet

v1 僅支援：

- 單一 parquet 檔輸出

## 7. Self-description 能力

v1 也提供：

- dataset list
- schema metadata
- dataset availability

這些屬於 API 的 product surface，不只是內部實作輔助。

## 8. 當前實作狀態

目前已落地：

- runtime config
- query layer
- catalog
- services
- response schemas
- error handlers
- routers / app factory
- CLI runner

也就是說，v1 已可本機啟動並提供：

- `/v1`
- `/v1/info/*`
- `/v1/data/candles`
- `/v1/data/candles/export`
