# Info Endpoints

本文件描述 `serving_engine` v1 已落地的 `/v1/info/*` endpoints。

## 1. `GET /v1/info/version`

用途：

- 回傳 service 名稱、API version、目前支援的 datasets 與預設 schema version

response model：

- `VersionInfoResponse`

## 2. `GET /v1/info/datasets`

用途：

- 回傳支援的 dataset 清單與 capability metadata

response model：

- `SupportedDatasetsResponse`

目前 v1 僅有：

- `candles`

## 3. `GET /v1/info/schemas/{dataset}/{schema_version}`

用途：

- 回傳指定 dataset/schema_version 的 schema metadata

response model：

- `SchemaInfoResponse`

目前 v1 僅支援：

- `dataset=candles`
- `schema_version=v1`

## 4. `GET /v1/info/availability/candles`

query params：

- `symbol`：必填
- `exchange`：可選
- `interval`：可選

用途：

- 回傳 candles availability metadata

response model：

- `CandlesAvailabilityResponse | null`

注意：

- 無資料時直接回 `null`
- `available_end_ms` 採 end-exclusive 語意
- 第一版只回 `ms`，不加 ISO 欄位
