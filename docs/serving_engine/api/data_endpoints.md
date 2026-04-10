# Data Endpoints

本文件描述 `serving_engine` v1 已落地的 `/v1/data/*` endpoints。

## 1. `GET /v1/data/candles`

用途：

- 單 symbol JSON rows query

query params：

- `symbol`：必填
- `start`：必填，ISO8601，timezone-aware
- `end`：必填，ISO8601，timezone-aware
- `exchange`：可選
- `interval`：可選
- `limit`：可選

response model：

- `CandlesQueryResponse`

行為重點：

- 只支援單 symbol
- `row` 不帶 `symbol`
- `start/end` 在 service 內正規化成 UTC `...Z`
- 未提供 `limit` 時，會自動套 `json_query_max_rows`

## 2. `GET /v1/data/candles/export`

用途：

- candles parquet export

query params：

- `symbols`：必填，comma-separated string
- `start`：必填
- `end`：必填
- `exchange`：可選
- `interval`：可選

例子：

- `symbols=BTC-USDT-SWAP`
- `symbols=BTC-USDT-SWAP,ETH-USDT-SWAP`

response：

- `FileResponse`

目前 v1 固定：

- `application/octet-stream`
- 單一 parquet 檔
- router 只做 `split(",")`
- 真正的 normalize / trim / dedupe 在 service
